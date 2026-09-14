package cfd.ghostbin.ghostwebvpn

import android.app.Application

/** Initializes the WireGuard GoBackend before any UI or service touches the VPN. */
class GhostApp : Application() {
    override fun onCreate() {
        super.onCreate()
        VpnManager.initialize(this)
    }
}
