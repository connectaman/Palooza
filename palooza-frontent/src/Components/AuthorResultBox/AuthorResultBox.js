import React, { useEffect, } from 'react';
import "./AuthorResultBox.css";
import { Chip, Grid, Stack } from '@mui/material';
import MaterialToolTip from '@mui/material/Tooltip';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardContent from '@mui/material/CardContent';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import LanguageIcon from '@mui/icons-material/Language';
import EmailIcon from '@mui/icons-material/Email';

function AuthorResultBox({ author }) {

    return (
        <Grid item xs={4}>
            <Card style={{ "height": "100%", "display": "flex", "width": "100%", "flexDirection": "column", "justifyContent": "space-between", "textAlign": "left" }} >
                <CardHeader
                    avatar={
                        <Avatar alt={author.name} src={author.thumbnail} sx={{ width: 56, height: 56 }} />
                    }
                    action={
                        <Stack direction="row">
                            <MaterialToolTip title={author.email}>
                                <IconButton aria-label="Send Email">
                                    <EmailIcon />
                                </IconButton>
                            </MaterialToolTip>
                            <MaterialToolTip title={author.website}>
                                <IconButton aria-label="Visit Website">
                                    <LanguageIcon />
                                </IconButton>
                            </MaterialToolTip>
                        </Stack>

                    }
                    title={author.name}
                    titleTypographyProps={{ "fontSize": "1.5em", "fontWeight": "bold" }}
                    subheader={author.affiliations}
                    style={{ "justifyContent": "flex-start", "alignContent": "flex-start", "alignItems": "flex-start" }}
                />
                <CardContent>
                    <Grid container spacing={2} >
                        <Grid item xs={12} md={6}>
                            <Typography variant="body2" color="text.secondary">
                                Total Citations: {author.citations}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                H-Index: {author.h_index}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                i10: {author.i10_index}
                            </Typography>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <img src={"data:image/jpeg;charset=utf-8;base64," + author.graph} width="100%"/>
                        </Grid>
                    </Grid>

                    {author.interests && author.interests.map(interest => <Chip label={interest.title} color="primary" variant="outlined" sx={{ m: 0.5 }} size="small" />)}

                </CardContent>
            </Card>
        </Grid>
    )
}

export default AuthorResultBox