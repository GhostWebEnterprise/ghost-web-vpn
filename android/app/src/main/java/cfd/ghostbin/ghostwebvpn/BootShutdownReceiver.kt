package cfd.ghostbin.ghostwebvpn

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

/**
 * Restores the last tunnel state after reboot and marks the tunnel down on
 * shutdown. The WireGuard GoBackend's VpnService handles always-on VPN on its
 * own; this receiver covers the case where the user reconnected manually.
 */
class BootShutdownReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        val action = intent.action ?: return
        if (action == Intent.ACTION_BOOT_COMPLETED) {
            val repo = TunnelRepository(context)
            if (!repo.wasConnected()) return
            VpnManager.initialize(context.applicationContext)
            val pending = goAsync()
            CoroutineScope(SupervisorJob() + Dispatchers.IO).launch {
                try {
                    VpnManager.connect()
                } finally {
                    pending.finish()
                }
            }
        } else if (action == Intent.ACTION_SHUTDOWN) {
            TunnelRepository(context).setConnected(false)
        }
    }
}
