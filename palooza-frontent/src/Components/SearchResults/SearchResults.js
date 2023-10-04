import React, { createContext, useContext, useEffect, useState } from 'react';
import "./SearchResults.css";
import { Box, Button, Card, CardActions, CardContent, CardHeader, Grid, IconButton, Stack, Tab, Tabs, Tooltip, Typography } from '@mui/material';
import PropTypes from 'prop-types';

import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Slide from '@mui/material/Slide';
import DocumentScannerIcon from '@mui/icons-material/DocumentScanner';
import CategoryIcon from '@mui/icons-material/Category';
import FindInPageIcon from '@mui/icons-material/FindInPage';
import FavoriteIcon from '@mui/icons-material/Favorite';
import DownloadForOfflineIcon from '@mui/icons-material/DownloadForOffline';
import axios from 'axios';
import BASE_API_URL from '../../Config/config';
import CustomLoader from '../CustomLoader/CustomLoader';
import AuthorResultBox from '../AuthorResultBox/AuthorResultBox';
import CustomAccordion from '../CustomAccordion/CustomAccordion';
import CustomChatBot from '../CustomChatBot/CustomChatBot';
import CustomMindmap from '../CustomMindmap/CustomMindmap';
import AccountTreeIcon from '@mui/icons-material/AccountTree';

const Transition = React.forwardRef(function Transition(props, ref) {
    return <Slide direction="up" ref={ref} {...props} />;
});

const ExtractContext = createContext();

const SearchResultBox = ({ searchItem, searchInputVal }) => {
    const [showModal, setShowModal] = useState(false);
    const [modalType, setModalType] = useState("VisitPaper");
    const [isFav, setIsFav] = useState(false);
    const [currentPaperUrl, setCurrentPaperUrl] = useState("");
    const [currentPaperExtract, setCurrentPaperExtract] = useState("");
    const [paperAnalysisContent, setPaperAnalysisContent] = useState("");
    const [paperNER, setPaperNER] = useState("");
    const [isModalLoading, setIsModalLoading] = useState(false);
    const [mindmap, setMindmap] = useState([]);
    const extractMap = useContext(ExtractContext);

    const fetchPaperExtract = async (hideModal=true) => {
        try {
            const currentPaperExtract = extractMap.extractMap[currentPaperUrl];
            if (currentPaperExtract) {
                if(hideModal){setIsModalLoading(false);}
                return currentPaperExtract;
            }
        } catch (ex) {
            console.log(ex);
        }

        return await axios.post(BASE_API_URL + "/extract", { url: currentPaperUrl })
            .then((response) => {
                extractMap.updateExtractMap({ ...extractMap.extractMap, [currentPaperUrl]: response.data });
                if(hideModal){setIsModalLoading(false);}
                return response.data;
            })
            .catch((err) => {
                if(hideModal){setIsModalLoading(false);}
                console.log("Failed Response: " + err);
            })
    };

    const fetchPaperAnalysis = async (paperExtract) => {
        const searchQuery = localStorage.getItem("searchQuery");
        return await axios.post(BASE_API_URL + "/paperanalysis", { query: searchQuery, content: paperExtract })
            .then((response) => {
                setIsModalLoading(false);
                setPaperAnalysisContent(response.data);
                return response.data;
            }).catch((err) => {
                setIsModalLoading(false);
                console.log("Failed to Analyze Paper: " + err);
            })
    };

    const fetchNER = async (paperExtract) => {
        if (paperNER != null && paperNER != "") {
            setIsModalLoading(false);
            return paperNER;
        }
        const searchQuery = localStorage.getItem("searchQuery");
        return await axios.post(BASE_API_URL + "/ner", { content: paperExtract, query: searchQuery })
            .then((response) => {
                setPaperNER(response.data);
                return response.data;
            }).catch((err) => {
                console.log("Failed to Fetch NER: " + err);
            }).finally(() => { setIsModalLoading(false); })
    }

    const handleExtractPaper = async () => {
        setIsModalLoading(true);
        setModalType("ExtractPaper");
        setShowModal(true);
        const paperExtract = await fetchPaperExtract();

    };

    const handleAnalyzePaper = async () => {
        setIsModalLoading(true);
        setModalType("AnalyzePaper");
        setShowModal(true);
        const paperExtract = await fetchPaperExtract(false);
        await fetchPaperAnalysis(paperExtract);
    };

    const handleNER = async () => {
        setIsModalLoading(true);
        setModalType("NER");
        setShowModal(true);
        const paperExtract = await fetchPaperExtract();
        fetchNER(paperExtract);
    };

    const handleDownloadPaperReport = () => {
        if (paperAnalysisContent) {
            // create file in browser
            const fileName = "paper-analysis";
            const json = JSON.stringify(paperAnalysisContent, null, 2);
            const blob = new Blob([json], { type: "application/json" });
            const href = URL.createObjectURL(blob);

            // create "a" HTLM element with href to file
            const link = document.createElement("a");
            link.href = href;
            link.download = fileName + ".json";
            document.body.appendChild(link);
            link.click();

            // clean up "a" element & remove ObjectURL
            document.body.removeChild(link);
            URL.revokeObjectURL(href);
        }
    };

    const handleModalClose = () => {
        setShowModal(false);
    };

    const handleSetFavorite = () => {
        setIsFav(!isFav);
    }

    const fetchMindmap = async (paperTitle) => {
        return await axios.post(BASE_API_URL + "/mindmap", { query: paperTitle })
            .then((response) => {
                setMindmap(response.data);
                return response.data;
            }).catch((err) => {
                console.log("Failed to Fetch Mindmap: " + err);
            }).finally(() => { setIsModalLoading(false); })
    }

    const handleMindmap = (paperTitle) => {
        setIsModalLoading(true);
        setModalType("Mindmap");
        setShowModal(true);
        fetchMindmap(paperTitle);
    }

    const getModalTitle = () => {
        switch (modalType) {
            case "VisitPaper":
                return "Visit Paper"
            case "ExtractPaper":
                return "Extract Paper"
            case "CheckSimilarity":
                return "Check Similarity"
            case "GenerateLiterature":
                return "Generate Literature"
            case "AnalyzePaper":
                return "Analyze Paper"
            case "AskQnA":
                return "Ask Question and Answers"
            case "NER":
                return "Keyword Analysis"
            case "Mindmap":
                return "Mindmap";
            default:
                return modalType
        }
    };

    const getLoadingLabel = () => {
        switch (modalType) {
            case "ExtractPaper":
                return "Extracting Paper...";
            case "AnalyzePaper":
                return "Analyzing Paper...";
            case "NER":
                return "Extracting Keyword Analysis...";
            case "Mindmap":
                return "Generating Mindmap...";
            default:
                return "Loading...";
        }
    }

    const ExtractPaper = () => {
        return (
            <Typography variant="body1">
                {JSON.stringify(extractMap)}
            </Typography>
        )
    }

    const CustomChatMessageHandler = async (msg) => {
        return await axios.post(BASE_API_URL + "/paperqna", { content: currentPaperExtract, query: msg })
            .then((response) => {
                return response.data;
            })
            .catch((err) => {
                console.log("Failed to Handle Chat Msg: " + err);
                return "Something went wrong! Try again later!";
            })
    }

    const AnalyzePaper = () => {
        return (
            <>
                <Grid container spacing={2}>
                    <Grid item xs={6}>
                        {
                            paperAnalysisContent.analysis && Object.keys(paperAnalysisContent.analysis).map((analysis_key, aindex) => <CustomAccordion header={analysis_key} body={paperAnalysisContent.analysis[analysis_key]} key={aindex} />)
                        }
                        <CustomAccordion header={"Literature"} body={paperAnalysisContent.literature} alwaysCollapsed={true} />
                        <CustomAccordion header={"Similarity"} body={paperAnalysisContent.similar} alwaysCollapsed={true} />
                    </Grid>
                    <Grid item xs={6}>
                        <CustomChatBot msgHandler={CustomChatMessageHandler} />
                    </Grid>
                </Grid>
            </>
        )
    }

    const NER = () => {
        return (
            <div dangerouslySetInnerHTML={{ __html: paperNER }}></div>
        )
    }

    useEffect(() => {
        setCurrentPaperUrl(searchItem["Url of paper"]);
        setCurrentPaperExtract(extractMap.extractMap[currentPaperUrl])
    }, [currentPaperUrl]);

    return (
        <>
            <Grid item xs={4}>
                <Card className={"SearchResultCard" + (isFav ? " FavoriteCard" : "")} style={{ "height": "100%", "display": "flex", "width": "100%", "flexDirection": "column", "justifyContent": "space-between" }}>
                    <CardHeader
                        title={
                            <Typography variant="h6" component="div" className="SearchResultPaperTitle">
                                Paper Title: {searchItem["Paper Title"]}
                            </Typography>
                        }
                        subheader={
                            <Typography sx={{ mb: 1.5 }} color="text.secondary">
                                Author: {searchItem["Author"]}
                            </Typography>
                        }
                        action={
                            <Tooltip title="Add to Favorite">
                                <IconButton aria-label="favorite" onClick={handleSetFavorite}>
                                    <FavoriteIcon sx={{ color: isFav ? "red" : "black" }} />
                                </IconButton>
                            </Tooltip>
                        }
                        className="SearchResultCardHeader"
                    />
                    <CardContent>
                        <Typography variant="body2" className="SearchResultAbstract">
                            Paper Abstract: {searchItem["Paper Abstract"]}
                        </Typography>
                        <Typography sx={{ mb: 0.5, mt: 1.5 }} color="text.secondary">
                            Year: {searchItem["Year"]}
                        </Typography>
                        <Typography sx={{ mb: 0.5, mt: 0.5 }} color="text.secondary">
                            Publication: {searchItem["Publication"]}
                        </Typography>
                        <Typography sx={{ mb: 0, mt: 0.5 }} color="text.secondary">
                            Citation: {searchItem["Citation"]}
                        </Typography>
                    </CardContent>
                    <CardActions style={{justifyContent: "center"}}>
                        <Stack direction="row" spacing={2}>
                            <Tooltip title="Extract Paper">
                                <IconButton onClick={handleExtractPaper} color="primary">
                                    <DocumentScannerIcon />
                                </IconButton>
                            </Tooltip>

                            <Tooltip title="Analyze Paper">
                                <IconButton onClick={handleAnalyzePaper} color="warning">
                                    <FindInPageIcon />
                                </IconButton>
                            </Tooltip>

                            <Tooltip title="Keyword Analysis">
                                <IconButton onClick={handleNER} color="success">
                                    <CategoryIcon />
                                </IconButton>
                            </Tooltip>

                            <Tooltip title="Generate Mindmap">
                                <IconButton onClick={() => { handleMindmap(searchItem["Paper Title"]) }} color="secondary">
                                    <AccountTreeIcon />
                                </IconButton>
                            </Tooltip>
                        </Stack>

                    </CardActions>
                </Card>
            </Grid>
            <Dialog
                open={showModal}
                TransitionComponent={Transition}
                keepMounted
                onClose={handleModalClose}
                aria-describedby="searchResultModal"
                fullWidth={true}
                maxWidth="xl"
            >
                <DialogTitle>{getModalTitle()}</DialogTitle>
                {modalType == "AnalyzePaper" ? <Button
                    disabled={isModalLoading}
                    startIcon={<DownloadForOfflineIcon />}
                    variant="outlined"
                    onClick={handleDownloadPaperReport}
                    sx={{
                        position: 'absolute',
                        right: 8,
                        top: 8,
                    }}
                >
                    Download
                </Button> : <></>}
                <DialogContent>
                    <DialogContentText id="searchResultModal">
                        {isModalLoading ? <CustomLoader style={{ margin: "50px" }} label={getLoadingLabel()} /> : <>
                            {modalType == "ExtractPaper" ? <ExtractPaper /> : <></>}
                            {modalType == "AnalyzePaper" ? <AnalyzePaper /> : <></>}
                            {modalType == "NER" ? <NER /> : <></>}
                            {modalType == "Mindmap" ? <CustomMindmap mindmap={mindmap} /> : <></>}
                        </>}
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleModalClose}>Close</Button>
                </DialogActions>
            </Dialog>
        </>
    )
};

const WebSearchResult = ({ searchResults }) => {
    return (
        <Typography variant="h6" className="WebSearchResult">{searchResults}</Typography>
    )
};

function CustomTabPanel(props) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{ p: 3 }}>
                    <Typography>{children}</Typography>
                </Box>
            )}
        </div>
    );
}

CustomTabPanel.propTypes = {
    children: PropTypes.node,
    index: PropTypes.number.isRequired,
    value: PropTypes.number.isRequired,
};

function a11yProps(index) {
    return {
        id: `simple-tab-${index}`,
        'aria-controls': `simple-tabpanel-${index}`,
    };
}

const SearchResultContainer = ({ searchResults, searchInputVal, searchTrend }) => {
    const [tabCnt, setTabCnt] = useState(0);

    const handleTabChange = (event, newVal) => {
        setTabCnt(newVal)
    };
    return (
        <>
            <Box sx={{ width: '100%' }} className="SearchResultContainer">
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={tabCnt} onChange={handleTabChange} aria-label="Search Results">
                        <Tab label="Search Results" {...a11yProps(0)} />
                        <Tab label="Authors Analysis" {...a11yProps(1)} />
                        <Tab label="Topic Analysis" {...a11yProps(2)} />
                    </Tabs>
                </Box>
                <CustomTabPanel value={tabCnt} index={0}>
                    <Grid container spacing={2} padding={2}>
                        {searchResults && searchResults.paper && searchResults.paper.map(searchItem => <SearchResultBox searchItem={searchItem} searchInputVal={searchInputVal} />)}
                    </Grid>
                </CustomTabPanel>
                <CustomTabPanel value={tabCnt} index={1}>
                    <Grid container spacing={2} padding={2}>
                        {searchResults && searchResults.author && searchResults.author.map(author => <AuthorResultBox author={author} />)}
                    </Grid>
                </CustomTabPanel>
                <CustomTabPanel value={tabCnt} index={2} style={{ textAlign: "center" }}>
                    {searchTrend && searchTrend.timeseries ? <img src={"data:image/jpeg;charset=utf-8;base64," + searchTrend.timeseries} width="70%" height="500px" /> : <></>}
                    {searchTrend && searchTrend.reason ? <Typography variant="body1" sx={{ mt: 5 }}>{searchTrend.reason}</Typography> : <></>}
                </CustomTabPanel>
            </Box>

        </>
    )
};

const WebResultContainer = ({ isDataSearch, isWebSearch, searchResults }) => {
    return (
        <div className="WebResultContainer">
            {isDataSearch ? <Button startIcon={<DownloadForOfflineIcon />} variant="outlined">Download</Button> : <></>}
            <WebSearchResult searchResults={searchResults} />
        </div>
    )
};

const SearchResults = ({ isLoading, searchInputVal, searchResults, isDataSearch, isWebSearch, searchTrend }) => {
    const updateExtractMap = (newExtractMap) => {
        setExtractMap((originalExtractMap) => ({
            extractMap: newExtractMap,
            updateExtractMap
        }));
    }

    const [extractMap, setExtractMap] = useState({
        extractMap: {},
        updateExtractMap
    });

    const CustomLoaderContainer = () => {
        const CustomLoadingLabel = () => {
            return (
                <Typography sx={{ color: "white" }}>Searching...</Typography>
            )
        }

        return (
            <>
                <CustomLoader label={<CustomLoadingLabel />} />
            </>
        )
    }

    const CustomSearchResultBox = ({ searchTrend }) => {
        return (
            <>
                {(!isDataSearch && !isWebSearch) ? <SearchResultContainer searchResults={searchResults} searchInputVal={searchInputVal} searchTrend={searchTrend} /> : <WebResultContainer isDataSearch={isDataSearch} isWebSearch={isWebSearch} searchResults={searchResults} />}
            </>
        )
    }

    return (
        <ExtractContext.Provider value={extractMap}>
            {isLoading ? <CustomLoaderContainer /> : <CustomSearchResultBox searchTrend={searchTrend} />}
        </ExtractContext.Provider>
    )
}

export default SearchResults;