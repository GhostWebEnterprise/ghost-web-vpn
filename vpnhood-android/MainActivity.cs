using Android.App;
using Android.Content;
using Android.OS;
using Android.Views;
using Android.Widget;
using VpnHood.Client;
using VpnHood.Client.Device.Droid;
using VpnHood.Client.Device.Droid.ActivityEvents;
using VpnHood.Common.Tokens;

namespace GhostWeb.VpnHood.Android;

[Activity(Label = "GhostWeb VPN", MainLauncher = true, Exported = true, Icon = "@drawable/ghostweb_vpn_logo")]
public class MainActivity : ActivityEvent
{
    private EditText? _accessKeyInput;
    private Button? _connectButton;
    private TextView? _status;
    private bool _destroyed;

    protected override void OnCreate(Bundle? savedInstanceState)
    {
        base.OnCreate(savedInstanceState);

        var layout = new LinearLayout(this)
        {
            Orientation = Orientation.Vertical
        };
        layout.SetPadding(32, 48, 32, 32);

        layout.AddView(new TextView(this)
        {
            Text = "GhostWeb VPN",
            TextSize = 24
        });

        layout.AddView(new TextView(this)
        {
            Text = "Paste an access key from a VpnHood server you trust. No server or access key is bundled."
        });

        _accessKeyInput = new EditText(this)
        {
            Hint = "VpnHood access key",
            InputType = global::Android.Text.InputTypes.ClassText | global::Android.Text.InputTypes.TextVariationPassword,
        };
        _accessKeyInput.SetSingleLine(true);
        layout.AddView(_accessKeyInput, new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MatchParent,
            ViewGroup.LayoutParams.WrapContent));

        _status = new TextView(this) { Text = "Disconnected" };
        layout.AddView(_status);

        _connectButton = new Button(this) { Text = "Connect" };
        _connectButton.Click += async (_, _) => await ToggleConnectionAsync();
        layout.AddView(_connectButton);

        SetContentView(layout);
        AttachExistingClient();
    }

    protected override void OnResume()
    {
        base.OnResume();
        var client = VpnHoodClientSession.Client;
        if (client is not null)
            UpdateStatus($"VPN state: {client.State}");
    }

    private async Task ToggleConnectionAsync()
    {
        if (_connectButton is not null)
            _connectButton.Enabled = false;

        await VpnHoodClientSession.OperationLock.WaitAsync();
        try
        {
            if (_destroyed)
                return;

            var connectedClient = VpnHoodClientSession.Client;
            if (connectedClient is not null)
            {
                connectedClient.StateChanged -= OnClientStateChanged;
                if (await TryDisposeClientAsync(connectedClient))
                {
                    VpnHoodClientSession.ClearClient(connectedClient);
                    UpdateStatus("Disconnected");
                }
                else
                {
                    connectedClient.StateChanged += OnClientStateChanged;
                    UpdateStatus("Disconnect failed; VPN state is unknown. Retry disconnect before reconnecting.");
                }
                return;
            }

            var accessKey = _accessKeyInput?.Text?.Trim();
            if (string.IsNullOrWhiteSpace(accessKey))
            {
                UpdateStatus("Enter a VpnHood access key from a server you trust.");
                return;
            }

            UpdateStatus("Preparing VPN permission and packet capture…");
            var token = Token.FromAccessKey(accessKey);
            var packetCapture = await VpnHoodClientSession.Device.CreatePacketCapture(
                new AndroidUiContext(this));
            var client = new VpnHoodClient(
                packetCapture,
                GetOrCreateClientId(),
                token,
                new ClientOptions());

            VpnHoodClientSession.SetClient(client);
            client.StateChanged += OnClientStateChanged;
            UpdateStatus($"VPN state: {client.State}");
            await client.Connect();
            UpdateStatus($"VPN state: {client.State}");
        }
        catch (Exception)
        {
            var failedClient = VpnHoodClientSession.Client;
            if (failedClient is not null)
            {
                failedClient.StateChanged -= OnClientStateChanged;
                if (await TryDisposeClientAsync(failedClient))
                {
                    VpnHoodClientSession.ClearClient(failedClient);
                    UpdateStatus("Connection failed. Check the access key and server, then retry.");
                }
                else
                {
                    failedClient.StateChanged += OnClientStateChanged;
                    UpdateStatus("Connection failed and cleanup failed; VPN state is unknown. Retry disconnect before reconnecting.");
                }
            }
            else
            {
                UpdateStatus("Connection failed. Check the access key and server, then retry.");
            }
        }
        finally
        {
            VpnHoodClientSession.OperationLock.Release();
            if (_connectButton is not null && !_destroyed)
            {
                _connectButton.Enabled = true;
                _connectButton.Text = VpnHoodClientSession.Client is null ? "Connect" : "Disconnect";
            }
        }
    }

    private void AttachExistingClient()
    {
        var client = VpnHoodClientSession.Client;
        if (client is null)
            return;

        client.StateChanged -= OnClientStateChanged;
        client.StateChanged += OnClientStateChanged;
        UpdateStatus($"VPN state: {client.State}");
    }

    private async Task<bool> TryDisposeClientAsync(VpnHoodClient client)
    {
        try
        {
            await client.DisposeAsync();
            return true;
        }
        catch (Exception ex)
        {
            global::Android.Util.Log.Error(
                "GhostWebVpn",
                $"VpnHood client cleanup failed ({ex.GetType().Name}).");
            return false;
        }
    }

    private void OnClientStateChanged(object? sender, EventArgs e)
    {
        if (_destroyed)
            return;

        var client = VpnHoodClientSession.Client;
        var message = client is null ? "Disconnected" : $"VPN state: {client.State}";
        RunOnUiThread(() =>
        {
            if (!_destroyed)
                UpdateStatus(message);
        });
    }

    private string GetOrCreateClientId()
    {
        var preferences = GetSharedPreferences("ghostweb-vpn", FileCreationMode.Private)!;
        var stored = preferences.GetString("client-id", null);
        if (Guid.TryParse(stored, out var clientId))
            return clientId.ToString("D");

        clientId = Guid.NewGuid();
        var editor = preferences.Edit();
        if (editor is not null)
            editor.PutString("client-id", clientId.ToString("D"))?.Apply();
        return clientId.ToString("D");
    }

    private void UpdateStatus(string message)
    {
        if (_destroyed)
            return;

        if (_status is not null)
            _status.Text = message;
        if (_connectButton is not null)
            _connectButton.Text = VpnHoodClientSession.Client is null ? "Connect" : "Disconnect";
    }

    protected override void OnDestroy()
    {
        _destroyed = true;
        var client = VpnHoodClientSession.Client;
        if (client is not null)
            client.StateChanged -= OnClientStateChanged;

        // The app-scoped session owns the tunnel. Activity recreation only detaches
        // this UI observer; explicit user disconnect remains the only normal stop path.
        base.OnDestroy();
    }
}
