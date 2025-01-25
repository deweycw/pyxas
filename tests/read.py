from pyxas.scan import Scan, ScanGroup
from pyxas.background import Background as bg

if __name__ ==  '__main__':
    
    scan = Scan(data_file="/Users/christiandewey/Code/pyxas/tests/data/GP17_station5_19119_1cm_015_A.002")

    #scan.plot_mu()

    #scan.plot_each_channel()
    
    #scan.drop_bad_channels(channels_to_drop=['SCA1_5','SCA1_25'])

    #scan.plot_each_channel()

    group = ScanGroup(directory="/Users/christiandewey/Code/pyxas/tests/data/", base_name="GP17_station5_19119_1cm_015_A.")

    group.drop_bad_channels(channels_to_drop=['SCA1_5','SCA1_25'])

    group.average_scans()

    group.plot_averaged_mu()

    group.subtract_postedge(post_edge_range_E=(7155,8000))
    group.subtract_preedge(pre_edge_range_E=(6800,7090))

    group.plot_background_subtracted_mu()