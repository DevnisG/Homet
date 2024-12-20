using Microsoft.AspNetCore.Mvc;
using LibreHardwareMonitor.Hardware;

[ApiController]
[Route("api/[controller]")]
public class HardwareController : ControllerBase
{
    private readonly Computer _computer;

    public HardwareController()
    {
        _computer = new Computer
        {
            IsCpuEnabled = true,
            IsBatteryEnabled = true
        };
        _computer.Open();
    }

    [HttpGet("cpu")]
    public IActionResult GetCpuSensors() => GetHardwareData(HardwareType.Cpu, "No se detectaron datos del CPU.");

    [HttpGet("battery")]
    public IActionResult GetBatterySensors() => GetHardwareData(HardwareType.Battery, "No se detectaron baterías.");

    [HttpPost("off")]
    public IActionResult Off()
    {
        try
        {
            _computer.Close(); 

            GC.Collect(); 
            GC.WaitForPendingFinalizers();

            return Ok("El sistema se ha cerrado correctamente.");
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"Error al cerrar el sistema: {ex.Message}");
        }
    }

    private IActionResult GetHardwareData(HardwareType type, string notFoundMessage)
    {
        try
        {
            var hardwareData = _computer.Hardware
                .Where(h => h.HardwareType == type)
                .Select(hardware =>
                {
                    hardware.Update(); 
                    return new
                    {
                        HardwareName = hardware.Name,
                        Sensors = hardware.Sensors.Select(s => new
                        {
                            SensorName = s.Name,
                            Value = s.Value,
                            SensorType = s.SensorType.ToString()
                        }).ToList()
                    };
                }).ToList();

            if (!hardwareData.Any())
            {
                return NotFound(notFoundMessage);
            }

            return Ok(hardwareData);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"Error al obtener datos de hardware: {ex.Message}");
        }
    }
}
