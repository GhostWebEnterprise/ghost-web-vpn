package cfd.ghostbin.ghostwebvpn

import android.content.Context
import android.util.Log
import com.wireguard.android.backend.Backend
import com.wireguard.android.backend.GoBackend
import com.wireguard.config.Config
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext

/** Connection status exposed to the UI and the quick-settings tile. */
enum class VpnState { DISCONNECTED, CONNECTING, CONNECTED, FAILED }

/**
 * Singleton wrapper around the WireGuard GoBackend. Owns the single
 * tunnel instance and exposes its state as a StateFlow so MainActivity
 * and QuickTileService stay in sync without polling.
 */
object VpnManager {

    private const val TAG = "VpnManager"

    private lateinit var backend: Backend
    private lateinit var tunnel: com.wireguard.android.backend.Tunnel
    private lateinit var repository: TunnelRepository

    private val mutableState = MutableStateFlow(VpnState.DISCONNECTED)
    val state: StateFlow<VpnState> = mutableState.asStateFlow()

    private var initialized = false

    /** Must be called once from Application.onCreate before any connect attempt. */
    fun initialize(context: Context) {
        if (initialized) return
        val appContext = context.applicationContext
        repository = TunnelRepository(appContext)
        backend = GoBackend(appContext)
        tunnel = object : com.wireguard.android.backend.Tunnel {
            override fun getName() = repository.configName()
            override fun onStateChange(newState: com.wireguard.android.backend.Tunnel.State) {
                mutableState.value =
                    if (newState == com.wireguard.android.backend.Tunnel.State.UP) {
                        VpnState.CONNECTED
                    } else {
                        VpnState.DISCONNECTED
                    }
            }
        }
        initialized = true

        // Restore visual state if the VPN was left connected by the system
        // (always-on VPN) while the app process was dead.
        runCatching {
            val running = backend.runningTunnelNames.contains(tunnel.name)
            mutableState.value = if (running) VpnState.CONNECTED else VpnState.DISCONNECTED
            repository.setConnected(running)
        }
    }

    /**
     * Brings the tunnel up with the stored config. The VpnService permission
     * dialog is shown by the system on the first connect; this call throws
     * [BackendException] with reason VPN_NOT_AUTHORIZED if it is declined.
     */
    suspend fun connect(): VpnState = withContext(Dispatchers.IO) {
        check(initialized) { "VpnManager not initialized" }
        val config = repository.loadConfig()
            ?: run {
                mutableState.value = VpnState.FAILED
                return@withContext VpnState.FAILED
            }
        mutableState.value = VpnState.CONNECTING
        try {
            val newState = backend.setState(
                tunnel,
                com.wireguard.android.backend.Tunnel.State.UP,
                config
            )
            repository.setConnected(
                newState == com.wireguard.android.backend.Tunnel.State.UP
            )
            mutableState.value =
                if (newState == com.wireguard.android.backend.Tunnel.State.UP) {
                    VpnState.CONNECTED
                } else {
                    VpnState.DISCONNECTED
                }
            mutableState.value
        } catch (e: Exception) {
            Log.e(TAG, "connect failed", e)
            mutableState.value = VpnState.FAILED
            VpnState.FAILED
        }
    }

    /** Tears the tunnel down. */
    suspend fun disconnect(): VpnState = withContext(Dispatchers.IO) {
        check(initialized) { "VpnManager not initialized" }
        try {
            backend.setState(tunnel, com.wireguard.android.backend.Tunnel.State.DOWN, null)
        } catch (e: Exception) {
            Log.e(TAG, "disconnect failed", e)
        }
        repository.setConnected(false)
        mutableState.value = VpnState.DISCONNECTED
        mutableState.value
    }

    /** Connect when down, disconnect when up. Used by the tile and the big button. */
    suspend fun toggle(): VpnState =
        if (state.value == VpnState.CONNECTED) disconnect() else connect()

    /** Traffic counters and latest handshake for the stats screen. */
    data class Stats(val totalRx: Long, val totalTx: Long, val handshakeEpochMs: Long)

    fun stats(): Stats? {
        if (!initialized) return null
        val statistics = runCatching { backend.getStatistics(tunnel) }.getOrNull() ?: return null
        val peerStats = statistics.peers().firstOrNull()?.let { statistics.peer(it) }
        return Stats(
            totalRx = statistics.totalRx(),
            totalTx = statistics.totalTx(),
            handshakeEpochMs = peerStats?.latestHandshakeEpochMillis() ?: 0L
        )
    }

    fun repository(): TunnelRepository = repository
}
