using System.Diagnostics;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

var app = builder.Build();

app.UseHttpsRedirection();
app.MapControllers();

AddFirewallRule(5123);

app.Run();

static void AddFirewallRule(int port)
{
    try
    {
        var ruleName = $"Allow_Port_{port}";
        var checkProcess = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "netsh",
                Arguments = $"advfirewall firewall show rule name=\"{ruleName}\"",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                Verb = "runas"
            }
        };

        checkProcess.Start();
        string output = checkProcess.StandardOutput.ReadToEnd();
        checkProcess.WaitForExit();

        if (output.Contains("No rules match the specified criteria"))
        {
            Console.WriteLine("Rule does not exist. Adding rule...");
            var addProcess = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = "netsh",
                    Arguments = $"advfirewall firewall add rule name=\"{ruleName}\" dir=in action=allow protocol=TCP localport={port}",
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    Verb = "runas"
                }
            };

            addProcess.Start();
            string addOutput = addProcess.StandardOutput.ReadToEnd();
            addProcess.WaitForExit();

            Console.WriteLine(addOutput);
        }
        else
        {
            Console.WriteLine("Firewall rule already exists.");
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error: {ex.Message}");
    }
}

