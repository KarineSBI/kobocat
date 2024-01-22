cd `dirname $0`
ROOT_PATH=`pwd`
java -Xms256M -Xmx1024M -cp .:$ROOT_PATH:$ROOT_PATH/../lib/routines.jar:$ROOT_PATH/../lib/advancedPersistentLookupLib-1.2.jar:$ROOT_PATH/../lib/commons-collections-3.2.2.jar:$ROOT_PATH/../lib/commons-collections4-4.1.jar:$ROOT_PATH/../lib/dom4j-1.6.1.jar:$ROOT_PATH/../lib/external_sort.jar:$ROOT_PATH/../lib/geronimo-stax-api_1.0_spec-1.0.1.jar:$ROOT_PATH/../lib/ini4j-0.5.1.jar:$ROOT_PATH/../lib/jakarta-oro-2.0.8.jar:$ROOT_PATH/../lib/jboss-serialization.jar:$ROOT_PATH/../lib/log4j-1.2.15.jar:$ROOT_PATH/../lib/log4j-1.2.16.jar:$ROOT_PATH/../lib/mysql-connector-java-5.1.30-bin.jar:$ROOT_PATH/../lib/poi-3.16-20170419_modified_talend.jar:$ROOT_PATH/../lib/poi-ooxml-3.16-20170419_modified_talend.jar:$ROOT_PATH/../lib/poi-ooxml-schemas-3.16-20170419.jar:$ROOT_PATH/../lib/poi-scratchpad-3.16-20170419.jar:$ROOT_PATH/../lib/simpleexcel-1.2-20171120.jar:$ROOT_PATH/../lib/talend_file_enhanced_20070724.jar:$ROOT_PATH/../lib/talendcsv.jar:$ROOT_PATH/../lib/trove.jar:$ROOT_PATH/../lib/xmlbeans-2.6.0.jar:$ROOT_PATH/wf_climate_finance_0_1.jar:$ROOT_PATH/m_cdc_t_thematic_makers_frp_0_1.jar:$ROOT_PATH/m_cdc_t_working_groups_frp_0_1.jar:$ROOT_PATH/m_cdc_t_finance_working_groups_ups_0_1.jar:$ROOT_PATH/m_cdc_t_finance_sectors_ups_0_1.jar:$ROOT_PATH/m_cdc_t_sector_frp_0_1.jar:$ROOT_PATH/m_cdc_t_finance_sources_ups_0_1.jar:$ROOT_PATH/m_cdc_t_finance_thematic_makers_ups_0_1.jar:$ROOT_PATH/m_cdc_t_finances_ups_0_1.jar:$ROOT_PATH/m_cdc_t_sub_sectors_frp_0_1.jar:$ROOT_PATH/m_cdc_t_implement_agencies_frp_0_1.jar:$ROOT_PATH/m_cdc_t_finance_locations_ups_0_1.jar:$ROOT_PATH/lib_contextreader_0_1.jar:$ROOT_PATH/m_cdc_s_odadata_frp_0_1.jar:$ROOT_PATH/m_cdc_t_finance_implement_agencies_ups_0_1.jar: camclimate.wf_climate_finance_0_1.wf_CLIMATE_FINANCE  --context=PROD "$@"



echo "wf_CLIMATE_FINANCE is Done ."
echo "Hi, I'm sleeping for 300 seconds..."

sleep 300  


echo "Starting with wf_CDC_REPORT.."
#!/bin/sh
#cd `dirname $0`
cd /home/etl/wf_CDC_REPORT
ROOT_PATH=`pwd`
java -Xms256M -Xmx1024M -cp .:$ROOT_PATH:$ROOT_PATH/../lib/routines.jar:$ROOT_PATH/../lib/dom4j-1.6.1.jar:$ROOT_PATH/../lib/ini4j-0.5.1.jar:$ROOT_PATH/../lib/log4j-1.2.16.jar:$ROOT_PATH/../lib/mysql-connector-java-5.1.30-bin.jar:$ROOT_PATH/wf_cdc_report_0_1.jar:$ROOT_PATH/m_cdc_t_fr_finance_donor_l5y_frp_0_1.jar:$ROOT_PATH/m_cdc_t_fr_finance_ly_climate_change_by_thematic_level_frp_0_1.jar:$ROOT_PATH/m_cdc_t_finance_sector_l5y_frp_0_1.jar:$ROOT_PATH/lib_contextreader_0_1.jar:$ROOT_PATH/m_cdc_t_finance_ly_climate_change_by_thematic_level_frp_0_1.jar:$ROOT_PATH/m_cdc_t_finance_donor_l5y_frp_0_1.jar:$ROOT_PATH/m_cdc_temp_odadata_frp_0_1.jar:$ROOT_PATH/m_cdc_t_fr_finance_sector_l5y_frp_0_1.jar:$ROOT_PATH/m_cdc_t_geo_cambodia_top3levels_frp_0_1.jar: camclimate.wf_cdc_report_0_1.wf_CDC_REPORT  --context=PROD "$@" 
echo "All Done."
