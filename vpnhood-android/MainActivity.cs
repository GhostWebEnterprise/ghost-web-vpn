using Android.App;
using Android.OS;
using VpnHood.Core.Client.Devices.Android;

namespace GhostWeb.VpnHood.Android;

[Activity(Label = "GhostWeb VPN", MainLauncher = true, Exported = true)]
public class MainActivity : Activity
{
    protected override void OnCreate(Bundle? savedInstanceState)
    {
        base.OnCreate(savedInstanceState);
        _ = AndroidDevice.Create();
    }
}
