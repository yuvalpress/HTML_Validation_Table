$output = ""

foreach($server in $args) {
    if (Test-Connection -ComputerName $server -Count 1 -Quiet) {
        $nic = racadm -r $server -u root -p Customer1! getniccfg

        $output += (($nic | Select-String "IP Address")[0]).ToString().Split(" ")[13] + ","
        $output += (($nic | Select-String "Subnet Mask")[0]).ToString().Split(" ")[12] + ","
        $output += (($nic | Select-String "Gateway")[0]).ToString().Split(" ")[15] + ','

        $raid = (racadm -r $server -u root -p Customer1! raid get vdisks -o -p Layout)[7]
        if ( $raid -match 5) {
            $output += "5" + ","
        }
        elseif ($raid -match 6) {
            $output += "6" + ","
        }
        elseif ($raid -match 1) {
            $output += "1" + ","
        }
        elseif ($raid -match 0) {
            $output += "0" + ","
        } else:
            $output += '' + ','

        $output += ((racadm -r $server -u root -p Customer1! get idrac.VirtualConsole.plugintype)[8]).ToString().split("=")[1] + "," #Get vconsole settings

        $output += ((racadm -r $server -u root -p Customer1! getniccfg | Select-String "NIC Selection").ToString().Split("="))[1].Split(" ")[1] + "," #Get lom settings

        $output += (racadm -r $server -u root -p Customer1! getsvctag)[6] + "," #Get service tag

        $output += (racadm -r $server -u root -p Customer1! get iDRAC.Info.Name | Select-String "Name=").ToString().split("=")[1] #Get hostname

        $output += " next "
    } else {
        $output += "NoPing" + "," + "NoPing" + "," + "NoPing" + "," + "NoPing" + " next "
    }
}

Write-Output -NoNewline $output