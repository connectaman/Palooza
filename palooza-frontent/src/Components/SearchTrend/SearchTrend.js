import React from 'react';
import "./SearchTrend.css";
import { Grid } from '@mui/material';

function SearchTrend({searchTrend}) {
  return (
    <>
        {searchTrend ? <Grid container spacing={2}>
            <Grid item xs={6}></Grid>
            <Grid item xs={6}></Grid>
        </Grid> : <></>}
    </>
    
  )
}

export default SearchTrend