using Android.App;
using Android.OS;
using Android.Views;
using Android.Widget;
using VpnHood.Client;
using VpnHood.Client.Device.Droid;

namespace GhostWeb.VpnHood.Android;

[Activity(Label = "GhostWeb VPN", MainLauncher = true, Exported = true)]
public class MainActivity : Activity
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
            SingleLine = true
        };
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
            _client.OnStateChanged -= OnClientStateChanged;
            _client.Dispose();
            _client = null;
            UpdateStatus("Disconnected");
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
            var packetCapture = await _device!.CreatePacketCapture();
            var client = new VpnHoodClient(
                packetCapture,
                GetOrCreateClientId(),
                token,
                new ClientOptions());

            client.OnStateChanged += OnClientStateChanged;
            _client = client;
            UpdateStatus($"VPN state: {client.State}");
            await client.Connect();
            UpdateStatus($"VPN state: {client.State}");
        }
        catch (Exception ex)
        {
            _client?.Dispose();
            _client = null;
            UpdateStatus($"Connection failed: {ex.Message}");
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

    private void OnClientStateChanged(object? sender, EventArgs e)
    {
        RunOnUiThread(() => UpdateStatus(_client is null
            ? "Disconnected"
            : $"VPN state: {_client.State}"));
    }

    private Guid GetOrCreateClientId()
    {
        var preferences = GetSharedPreferences("ghostweb-vpn", FileCreationMode.Private)!;
        var stored = preferences.GetString("client-id", null);
        if (Guid.TryParse(stored, out var clientId))
            return clientId;

        clientId = Guid.NewGuid();
        preferences.Edit()?.PutString("client-id", clientId.ToString()).Apply();
        return clientId;
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
            _client.OnStateChanged -= OnClientStateChanged;
            _client.Dispose();
            _client = null;
        }

        base.OnDestroy();
    }
}
