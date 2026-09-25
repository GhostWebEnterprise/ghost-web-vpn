using Android.App;
using Android.OS;
using VpnHood.Client.Device.Android;

namespace GhostWeb.VpnHood.Android;

[Activity(Label = "GhostWeb VPN", MainLauncher = true, Exported = true)]
public class MainActivity : Activity
{
    protected override void OnCreate(Bundle? savedInstanceState)
    {
        base.OnCreate(savedInstanceState);
        _ = AndroidDevice.Current;
    }
}
