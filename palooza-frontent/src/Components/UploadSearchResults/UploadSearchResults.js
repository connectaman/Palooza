import React, { useEffect, useState } from 'react'
import { Card, CardContent, Grid, Typography } from '@mui/material';
import './UploadSearchResults.css';
import axios from 'axios';
import BASE_API_URL from '../../Config/config';
import CustomLoader from '../CustomLoader/CustomLoader';
import CustomAccordion from '../CustomAccordion/CustomAccordion';
import CustomChatBot from '../CustomChatBot/CustomChatBot';

function UploadSearchResults({ pdfPath, pdfFileName }) {
    const [getTitle, setGetTitle] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    const fetchGetTitle = async () => {
        await axios.post(BASE_API_URL + "/get-title", { filename: pdfFileName })
            .then((response) => {
                setGetTitle(response.data);
            })
            .catch((err) => {
                console.log("Failed to Get Title: " + err);
            })
            .finally(() => {
                setIsLoading(false);
            })
    };

    const UploadChatMessageHandler = async (msg) => {
        return await axios.post(BASE_API_URL + "/docqna", {filename: pdfFileName, query: msg})
            .then((response) => {
                return response.data;    
            })
            .catch((err) => {
                console.log("Failed to Handle Chat Msg: " + err);
                return "Something went wrong! Try again later!";
            })
    }

    useEffect(() => {
        setIsLoading(true);
        setGetTitle(null);
        fetchGetTitle();
    }, [pdfPath])
    return (
        <>
            <Grid container spacing={2} className="uploadSearchResultContainer" marginTop={3} sx={{padding: 2, pb: 5, mb: 5}}>
                <Grid item xs={6} className="previewContainer">
                    <iframe src={pdfPath} width="100%" height="600" />
                </Grid>
                <Grid item xs={6} className="resultsContainer">
                    {!isLoading && getTitle && Object.keys(getTitle).map((gkey, gindex) => <CustomAccordion header={gkey} body={getTitle[gkey]} key={gindex} />)}
                    {isLoading ? <CustomLoader label={<Typography variant="h6">Fetching Title...</Typography>} /> : <CustomChatBot msgHandler={UploadChatMessageHandler} />}
                </Grid>
            </Grid>
        </>

    )
}

export default UploadSearchResults;