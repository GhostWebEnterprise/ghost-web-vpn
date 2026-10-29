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

[Activity(Label = "GhostWeb VPN", MainLauncher = true, Exported = true)]
public class MainActivity : ActivityEvent
{
    private AndroidDevice? _device;
    private VpnHoodClient? _client;
    private EditText? _accessKeyInput;
    private Button? _connectButton;
    private TextView? _status;

    protected override void OnCreate(Bundle? savedInstanceState)
    {
        base.OnCreate(savedInstanceState);

        _device = AndroidDevice.Create();

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
    }

    private async Task ToggleConnectionAsync()
    {
        if (_client is not null)
        {
            var connectedClient = _client;
            if (_connectButton is not null)
                _connectButton.Enabled = false;

            connectedClient.StateChanged -= OnClientStateChanged;
            try
            {
                if (await TryDisposeClientAsync(connectedClient))
                {
                    if (ReferenceEquals(_client, connectedClient))
                        _client = null;
                    UpdateStatus("Disconnected");
                }
                else
                {
                    UpdateStatus("Disconnect failed; VPN state is unknown. Retry disconnect before reconnecting.");
                }
            }
            finally
            {
                if (_connectButton is not null)
                {
                    _connectButton.Enabled = true;
                    _connectButton.Text = _client is null ? "Connect" : "Disconnect";
                }
            }
            return;
        }

        var accessKey = _accessKeyInput?.Text?.Trim();
        if (string.IsNullOrWhiteSpace(accessKey))
        {
            UpdateStatus("Enter a VpnHood access key from a server you trust.");
            return;
        }

        if (_connectButton is not null)
            _connectButton.Enabled = false;

        try
        {
            UpdateStatus("Preparing VPN permission and packet capture…");
            var token = Token.FromAccessKey(accessKey);
            var packetCapture = await _device!.CreatePacketCapture(new AndroidUiContext(this));
            var client = new VpnHoodClient(
                packetCapture,
                GetOrCreateClientId(),
                token,
                new ClientOptions());

            client.StateChanged += OnClientStateChanged;
            _client = client;
            UpdateStatus($"VPN state: {client.State}");
            await client.Connect();
            UpdateStatus($"VPN state: {client.State}");
        }
        catch (Exception)
        {
            var failedClient = _client;
            if (failedClient is not null)
            {
                failedClient.StateChanged -= OnClientStateChanged;
                if (await TryDisposeClientAsync(failedClient))
                {
                    if (ReferenceEquals(_client, failedClient))
                        _client = null;
                    UpdateStatus("Connection failed. Check the access key and server, then retry.");
                }
                else
                {
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
            if (_connectButton is not null)
            {
                _connectButton.Enabled = true;
                _connectButton.Text = _client is null ? "Connect" : "Disconnect";
            }
        }
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
            global::Android.Util.Log.Error("GhostWebVpn", $"VpnHood client cleanup failed ({ex.GetType().Name}).");
            return false;
        }
    }

    private void OnClientStateChanged(object? sender, EventArgs e)
    {
        RunOnUiThread(() => UpdateStatus(_client is null
            ? "Disconnected"
            : $"VPN state: {_client.State}"));
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
        if (_status is not null)
            _status.Text = message;
        if (_connectButton is not null)
            _connectButton.Text = _client is null ? "Connect" : "Disconnect";
    }

    protected override void OnDestroy()
    {
        if (_client is not null)
        {
            var client = _client;
            _client = null;
            client.StateChanged -= OnClientStateChanged;
            _ = TryDisposeClientAsync(client);
        }

        base.OnDestroy();
    }
}
