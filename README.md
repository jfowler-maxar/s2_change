# s2_change
Input sentinel 2 imagery and detect change 

Change Detect Solo Project Workflow
Justin Fowler
last update 12/1/2023

1.access_sentinel_data dir: search_for_gran.py and download_seninel.py
    search_for_gran.py:
        input s2 gran, and exports to .csv all the s2 files that were in parameters
            parameters: start_date, end_date,gran,productType,data_collection,cloudcover (set to 10)

    manually select scenes:
        look through csv's and select ID,Name of scenes wanted
        Select as many scenes as needed
        can check Copernicus browser to see thumbnail of scenes

        save csv as {gran}_select.csv

        Improvements: csv's probably only need to include ID and Name when created in search_for_gran.py

    download_seninel.py:
        given {gran}_select.csv, download all scenes to tile directory
        currently can only download 3 at a time, have to rerun.

        Improvements: add a wait function after 3 have been downloaded, so don't have to rerun to get all


2. safe_dir_reorg.py
    Unzip .SAFE directories
    Create date directories for where data will be stored
    For L2A data creates MSIL2A directory, L1C data creates MSIL1C directory
        Copies .jp2 bands 2,3,4,8,11,12 and SCL to MSIL2A
        Copies .jp2 bands 2,3,4,8,11,12,8a,10 to MSIL1C
    Deletes unzip'd .SAFE directories

    Improvements:
        Lot's of looping, could search for specific files more efficiently

3. download_glo30.py
    Given tile name, uses sentinel_2_index_shapefile.shp to download GLO 30 dem from aws
    Downloads 1x1's and mosaic's them (with buffer) to sentinel 2 grid

    outputs:
        a. [gran]_glo30_buf.tif

    Improvements:
        Currently not using DEM, add terrain shadow calculation further downstream
        Came across a tile that covers 6 1x1's... so annoying

4. stack_vrt.py
    Takes MSIL2A directory and stacks bands 2,3,4,8,11,12 to 1,2,3,4,5,6
    Also uses SCL to mask out cloud mask and cloud shadow, set's nodata to -9999

    Outputs:
        a.  [tile]_[date]_6band.vrt
        b.  [tile]_[date]_6band_masked.tif

    stack_vrt_v2.py
        Set's up files to be in {tile}\{month}\{date} dir's
        To be immediately ready for mosaic_indiv_bands.py

4B. mosaic_images:
    reorg_date_to_month.py
    mosaic_indiv_bands.py
    mosaic_month.py
    Unmasked clouds are a real pain
    Plan:
        Download 1 scene per week (could do more but so much downloading...)
        after all the scenes are masked, mosaic all scenes in a month
        take the lowest value, missed clouds would be super high values theoretically
            potentially will miss change, but it should be caught the next month so no biggie

    Move all date dirs into yyyymm dirs, then go through and mosaic them based of yyyymm dirs


5.normalize_dif.py and create_indicies.py
    normalize_dif.py
        Creates functions
        norm_dif: create normalized differences, like ndvi.
            Clamps over |100|
            assumes -9999 as nodata
        msavi_calc: creates msavi
            Clamps over |100|
            assumes -9999

        Improvements:
            set up class correctly, with self as first input parameter
            make nodata an input parameter

    create_indicies
        Uses function in normalize_dif.py
        Loops through date directories, find's '_6band_masked.tif' and creates:

        Outputs:
            a.[tile]_[date]_ndvi.tif
            b.[tile]_[date]_ndwi.tif
            c.[tile]_[date]_ndbi.tif
            d.[tile]_[date]_ndsi.tif
            e.[tile]_[date]_msavi.tif

5B. Need to take ndwi's and mask out the masked.tif's again... maybe this should be done before...
    can be part of masked process, do it with stack_vrt.py.
    if part of mask, won't get water change...
    maybe, just use ndwi time series to mask out for stats in

6. stack_time.py and stack_bands_time.py
    stack_time.py:
        takes date indicies(5.a->e) and stacks them in a time seires vrt
        Output:
            a.time_series/[tile]_ndvi_stack.vrt
            b.time_series/[tile]_ndwi_stack.vrt
            c.time_series/[tile]_ndbi_stack.vrt
            d.time_series/[tile]_ndsi_stack.vrt
            e.time_series/[tile]_msavi_stack.vrt

    stack_bands_time.py:
        takes date 6band_masked.tif's (4.b) and stacks them in a time seires vrt
        Output:
            a.time_series/[tile]_b1_stack.tif
            b.time_series/[tile]_b2_stack.tif
            c.time_series/[tile]_b3_stack.tif
            d.time_series/[tile]_b4_stack.tif
            e.time_series/[tile]_b5_stack.tif
            f.time_series/[tile]_b6_stack.tif

    Improvements:
        Unsure if need 2 seperate scripts, or if need indicies time series at all

7. time_series_v2.py
    Takes stats for time_series stacks
    uses chips so doesnt destroy RAM

    Outputs:
    a. time_stats/[tile]_[timeseries]_mean.tif
    b. time_stats/[tile]_[timeseries]_median.tif
    c. time_stats/[tile]_[timeseries]_range.tif
    d. time_stats/[tile]_[timeseries]_std.tif


8. temporal_slope_v2.py
    take time_series and run linear regression on them, in order to determine temporal slope
    Uses 512x512 chips to process so doesn't destroy RAM
    numpy math to get linear regression slope

    Improvements:

9. std_tempslope.py
    create script to threshold based on standard deviation of temporal slope file
    add water/ocean mask to get rid of std being skewed?
        for water mask, use focal filters (check Geoprocessing with Python book)

10. step_time.py
    get date of change

11. For now, just taking Blue band, will have to come up with better, change algorthim/rules later
    a. vector_attrib/b1_change_layers.py
        combine's standard deviation of temp slope and step filter date
        Where std > |3|, keep the step filter date
        inputs:
            f'{gran}_b{bnum}_stacktempslope_std.tif')   #standard deviation layer
            f'{gran}_b{bnum}_date_num.tif'              #step filter detect layer
        output:
            f'{gran}_b{bnum}_ch_tmp.tif'#tmp till goes through sieve

    b. vector_attrib/ch_layer_sieve.py
        Remove single pixels (seems to only remove single pixels surrounded by 0s)
        input: f'{gran}_b{bnum}_ch_tmp.tif
        output: f'{gran}_b{bnum}_ch.tif'

        Improvements:
            play around more with gdal_sieve.py, figure out how to remove all single pixels

    c. vector_attrib/vectorize.py
        Use gdal.Polygonize to export raster to vector
        input: f'{gran}_b{bnum}_ch.tif'
        output: f'{gran}_b{bnum}_ch_tmp.shp'

        Looks like a bug? seeing a date=10, when the max should be 9...

12. Add attribution
    vec_attrib1.py
        uses rasterstats, zonal stats which takes forever

    vec_attrib_test2.py, uses centriod, point is much faster, but centriod might not be value inside poly
        slope_std, float
        veg_mean, veg or non veg
        veg_std, low/high variation
        water_std, low/high variation


    Future Attributes, layers not yet scripted
        max ndvi post change (veg regrowth)
        shadow likely hood
        brightness increase/decrease (high albedo buildings)
