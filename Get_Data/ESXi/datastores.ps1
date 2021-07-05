Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false 1>$null 2>$null #Set trust certificate for remote VSphere servers

Connect-VIServer -Server $args[0] -User root -Password customer1!

$datastoresCapacity = (Get-Datastore).CapacityGB
$outputCapacity = ''

foreach($r in $datastoresCapacity){
    if($r -ge 520) {
        $outputCapacity += [string][math]::Round($r /1024) + "T" + ','
    }
    else {
        $outputCapacity += [string]$r + "GB" + ','
    }
}

$outputCapacity = $outputCapacity -replace ".$" #Delete last coma

$datastores = (Get-Datastore).Name
$outputDatastore = ''

foreach($ds in $datastores) {
    $outputDatastore += $ds + ','
}

$outputDatastore = $outputDatastore -replace ".$" #Delete last coma

#Get storage adapters information
$devicesNames = ''
$targetsCount = ''
$devicesConunt = ''
$pathsCount = ''

foreach($hba in (Get-VMHostHba -Type "FibreChannel")){
    $target = ((Get-View $hba.VMhost).Config.StorageDevice.ScsiTopology.Adapter | Where-Object {$_.Adapter -eq $hba.Key}).Target
    $luns = Get-ScsiLun -Hba $hba  -LunType "disk"
    $nrPaths = ($target | ForEach-Object{$_.Lun.Count} | Measure-Object -Sum).Sum

    $devicesNames += [string]$hba.Device + ','
    $targetsCount += [string]$target.Count + ',' 
    $devicesConunt += [string]$luns.Count + ',' 
    $pathsCount += [string]$nrPaths + ','
}

$devicesNames = $devicesNames -replace ".$" #Delete last coma
$targetsCount = $targetsCount -replace ".$" #Delete last coma
$devicesConunt = $devicesConunt -replace ".$" #Delete last coma
$pathsCount = $pathsCount -replace ".$" #Delete last coma

Disconnect-VIServer -Server $args[0] -confirm:$false

Write-Output $outputDatastore
Write-Output $outputCapacity
Write-Output $devicesNames
Write-Output $targetsCount
Write-Output $devicesConunt
Write-Output $pathsCount