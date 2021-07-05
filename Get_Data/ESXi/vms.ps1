Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false 1>$null 2>$null #Set trust certificate for remote VSphere servers

Connect-VIServer -Server $args[0] -User root -Password password

$names = (Get-VM | Select-Object -Property Name,Guest,MemoryGB,NumCpu).Name
$outputNames = ''

if(($names | Measure-Object).Count -ne 0) {

    foreach($name in $names) {
        $outputNames += $name + ','
    }

    $outputNames = $outputNames -replace ".$" #Delete last coma

    $guests = (Get-VM | Select-Object -Property Name,Guest,MemoryGB,NumCpu).Guest.OSFullName
    $outputGuests = ''

    foreach($os in $guests) {
        $outputGuests += $os + ','
    }

    $outputGuests = $outputGuests -replace ".$" #Delete last coma

    $memories = (Get-VM | Select-Object -Property Name,Guest,MemoryGB,NumCpu).MemoryGB
    $outputMemories = ''

    foreach($memory in $memories) {
        $outputMemories += [string]$memory + 'GB' + ','
    }

    $outputMemories = $outputMemories -replace ".$" #Delete last coma

    $cores = (Get-VM | Select-Object -Property Name,Guest,MemoryGB,NumCpu).NumCpu
    $outputCores = ''

    foreach($core in $cores) {
        $outputCores += [string]$core + 'Cores' + ','
    }

    $outputCores = $outputCores -replace ".$" #Delete last coma
} else {
    $outputNames = 'false'
    $outputGuests = 'false'
    $outputMemories = 'false'
    $outputCores = 'false'
}

Disconnect-VIServer -Server $args[0] -confirm:$false

Write-Output $outputNames
Write-Output $outputGuests
Write-Output $outputMemories
Write-Output $outputCores


