package cfd.ghostbin.ghostwebvpn

import android.os.Build
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

/** Quick-settings tile: shows the live VPN state and toggles the tunnel. */
class QuickTileService : TileService() {

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var listening = false

    override fun onStartListening() {
        listening = true
        super.onStartListening()
        VpnManager.initialize(applicationContext)
        observeState()
        render()
    }

    override fun onStopListening() {
        listening = false
        super.onStopListening()
    }

    override fun onClick() {
        super.onClick()
        VpnManager.initialize(applicationContext)
        scope.launch { VpnManager.toggle() }
    }

    private var observed = false
    private fun observeState() {
        if (observed) return
        observed = true
        scope.launch {
            VpnManager.state.collectLatest {
                if (listening) render()
            }
        }
    }

    private fun render() {
        val tile = qsTile ?: return
        val connected = VpnManager.state.value == VpnState.CONNECTED
        tile.state = if (connected) Tile.STATE_ACTIVE else Tile.STATE_INACTIVE
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            tile.subtitle = getString(
                if (connected) R.string.tile_connected else R.string.tile_disconnected
            )
        }
        tile.updateTile()
    }

    override fun onDestroy() {
        scope.cancel()
        super.onDestroy()
    }
}
