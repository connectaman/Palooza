import React, { useEffect, useState } from 'react';
import "./UploadDataSearchResults.css";
import { Button, Grid } from '@mui/material';
import DownloadForOfflineIcon from '@mui/icons-material/DownloadForOffline';
import CustomChatBot from '../CustomChatBot/CustomChatBot';
import axios from 'axios';
import BASE_API_URL from '../../Config/config';
import { DataGrid } from '@mui/x-data-grid';
import Box from '@mui/material/Box';


function UploadDataSearchResults({ dataFileData }) {
    const [dataHeaders, setDataHeaders] = useState([]);
    const [dataRows, setDataRows] = useState([]);
    const [dataAnalysis, setDataAnalysis] = useState("");

    const fetchDataAnalysis = async () => {

        return await axios.post(BASE_API_URL + "/dataset-analysis", { dataset: "data.csv" })
            .then((response) => {
                setDataAnalysis(response.data);
                return response.data;
            })
            .catch((err) => {
                console.log("Failed to Fetch Data Analysis: " + err);
            })
    };

    const handleDownload = async () => {
        const dataAnalysisHtml = await fetchDataAnalysis();

        if (dataAnalysisHtml && dataAnalysisHtml != "") {
            const fileName = "data-analysis";
            const href = 'data:text/html;charset=UTF-8,' + encodeURIComponent(dataAnalysisHtml);

            // create "a" HTLM element with href to file
            const link = document.createElement("a");
            link.href = href;
            link.download = fileName + ".html";
            document.body.appendChild(link);
            link.click();

            // clean up "a" element & remove ObjectURL
            document.body.removeChild(link);
            URL.revokeObjectURL(href);
        }

    };

    const DataChatMessageHandler = async (msg) => {
        return await axios.post(BASE_API_URL + "/dataset-qna", { dataset: "data.csv", query: msg })
            .then((response) => {
                return response.data;
            })
            .catch((err) => {
                console.log("Failed to Handle Chat Msg: " + err);
                return "Something went wrong! Try again later!";
            })
    };

    useEffect(() => {
        if (dataFileData && dataFileData.length > 0) {
            const newDataHeaders = [];
            Object.keys(dataFileData[0]).map((item, index) => {
                newDataHeaders.push({
                    field: item, headerName: item
                });
            });
            setDataHeaders(newDataHeaders);
            const newDataRows = [];
            dataFileData.map((item, index) => {
                newDataRows.push({ ...item, id: index })
            });
            setDataRows(newDataRows);
        }
    }, [dataFileData])
    return (
        <>
            <Grid container spacing={2} className="uploadSearchResultContainer" marginTop={5} marginBottom={5} sx={{ padding: 2, pb: 5 }}>
                <Grid item xs={6} className="previewContainer" sx={{ padding: 2 }}>
                    <Box style={{backgroundColor: "white"}}>
                        <DataGrid
                            rows={dataRows}
                            columns={dataHeaders}
                            initialState={{
                                pagination: {
                                    paginationModel: { page: 0, pageSize: 5 },
                                },
                            }}
                            pageSizeOptions={[5, 10]}
                        />
                    </Box>
                </Grid>
                <Grid item xs={6} className="resultsContainer" sx={{ padding: 2 }}>
                    <Button variant="outlined" color="primary" startIcon={<DownloadForOfflineIcon />} onClick={handleDownload}>Download Dataset Analysis</Button>
                    <CustomChatBot msgHandler={DataChatMessageHandler} />
                </Grid>
            </Grid>
        </>
    )
}

export default UploadDataSearchResults