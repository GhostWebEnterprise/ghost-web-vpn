using VpnHood.Client;
using VpnHood.Client.Device.Droid;

namespace GhostWeb.VpnHood.Android;

/// <summary>
/// Owns the VpnHood client for the app process rather than a single Activity.
/// Android may recreate MainActivity during rotation or task restoration; that must
/// not silently tear down an established VPN tunnel.
/// </summary>
internal static class VpnHoodClientSession
{
    private static readonly object Sync = new();
    private static readonly Lazy<AndroidDevice> DeviceInstance = new(AndroidDevice.Create);
    private static VpnHoodClient? _client;

    public static SemaphoreSlim OperationLock { get; } = new(1, 1);

    public static AndroidDevice Device => DeviceInstance.Value;

    public static VpnHoodClient? Client
    {
        get
        {
            lock (Sync)
                return _client;
        }
    }

    public static void SetClient(VpnHoodClient client)
    {
        ArgumentNullException.ThrowIfNull(client);
        lock (Sync)
        {
            if (_client is not null && !ReferenceEquals(_client, client))
                throw new InvalidOperationException("A VpnHood client session is already active.");
            _client = client;
        }
    }

    public static bool ClearClient(VpnHoodClient client)
    {
        lock (Sync)
        {
            if (!ReferenceEquals(_client, client))
                return false;
            _client = null;
            return true;
        }
    }
}
