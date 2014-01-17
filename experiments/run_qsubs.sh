#!/bin/csh

set objective = "--obj-feas"
foreach n_min ( 10 10 10 10 )
    @ n_max = $n_min + 1

    #foreach objective ( --obj-feas --obj-social )
	foreach distribution ( --dist-urand-real --dist-correlated-real )
	    qsub -vN_MIN=${n_min},N_MAX=${n_max},OBJECTIVE=\"${objective}\",DISTRIBUTION=\"${distribution}\" qsub-general.sh
	    sleep 1
	end
    #end
end
