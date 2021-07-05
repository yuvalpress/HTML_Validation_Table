# Import-Module Vmware.PowerCLI -Verbose:$false | Out-Null #Import PowerCLI Module
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false 1>$null 2>$null #Set trust certificate for remote VSphere servers

$output = ''

foreach($server in $args) {
    #Connect to VSphere server
    Connect-VIServer -Server $server -Protocol https -User root -Password customer1! 1>$null 2>$null

    $output = $output + (((Get-VMHost).ExtensionData.Config.Network.Vnic | Where-Object{$_.Device -eq "vmk0"}).Spec.IP | Select-Object IpAddress, SubnetMask)[0].IpAddress + ','

    $output = $output + (((Get-VMHost).ExtensionData.Config.Network.Vnic | Where-Object{$_.Device -eq "vmk0"}).Spec.IP | Select-Object IpAddress, SubnetMask)[0].SubnetMask + ','

    $output = $output + (Get-VMHost).ExtensionData.Config.Network.IpRouteConfig.DefaultGateway    

    #disconnect from server
    Disconnect-VIServer -Server $server -Confirm:$false

    $output = $output + ' next '
}

# Write-Output($ip + ',' + $subnet + ',' + $gateway)
Write-Output -NoNewline $output