import { useEffect, useRef, useState } from "react";
import styled from "styled-components";
import axios from "axios";
import {
  Container,
  SearchInput,
  IconRightArrow,
  IconMagnifyingGlass
} from "./styles";
import Papa from "papaparse";

import Button from '@mui/material/Button';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import Stack from '@mui/material/Stack';
import UploadSearchResults from "../UploadSearchResults/UploadSearchResults";
import SearchResults from "../SearchResults/SearchResults";
import { Chip, FormControl, FormControlLabel, InputLabel, MenuItem, Select, Snackbar, Alert, Switch } from "@mui/material";
import UploadDataSearchResults from "../UploadDataSearchResults/UploadDataSearchResults";
import BASE_API_URL from "../../Config/config";

const Title = styled.p`
  font-size: 2rem;
  color: #eeeeee;
  letter-spacing: 0.15em;
  line-height: 2em;
`;

function Search({ searchStarted, searchTrigger, afterSearchTrigger }) {
  const targetRef = useRef(null);
  const [isHovered, setIsHovered] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const showSearchInput = searchStarted || isHovered || isFocused;
  const [searchInputVal, setSearchInputVal] = useState("");
  const fileInput = useRef(null);
  const dataFileInput = useRef(null);
  const [pdfPath, setPdfPath] = useState("");
  const [pdfFileName, setPdfFileName] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [showUploadSearchResults, setShowUploadSearchResults] = useState(false);
  const [dataFileData, setDataFileData] = useState([]);
  const [showUploadDataSearchResults, setShowUploadDataSearchResults] = useState(false);
  const [useWebSearch, setUseWebSearch] = useState(false);
  const [useDataSearch, setUseDataSearch] = useState(false);
  const [dataSource, setDataSource] = useState("all");
  const [isLoading, setIsLoading] = useState(false);
  const [showRequestError, setShowRequestError] = useState(false);
  const [searchTrend, setSearchTrend] = useState({});
  const [searchBarCollapsed, setSearchBardCollaped] = useState(false);

  useEffect(() => {
    targetRef.current.value = "";
  }, [showSearchInput]);

  const handleInputChange = (e) => {
    setSearchInputVal(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleFormSubmittion();
    }
  };

  const performCustomSearch = (val) => {
    targetRef.current.value = val;
    setSearchInputVal(val);
    handleFormSubmittion();
  }

  const fetchSearchTrend = () => {
    axios.post(BASE_API_URL + "/get-trend", {query: searchInputVal}).then((response) => {
      setSearchTrend(response.data);
    }).catch((err) => {
      console.log(err);
      setShowRequestError(true);
    });

  }

  const handleFormSubmittion = () => {
    searchTrigger();
    localStorage.setItem("searchQuery", searchInputVal);
    setShowUploadSearchResults(false);
    setShowUploadDataSearchResults(false);
    setShowSearchResults(true);
    setSearchBardCollaped(true);
    setIsLoading(true);
    fetchSearchTrend();
    axios.request({
      method: 'post',
      url: BASE_API_URL + "/scrape",
      headers: {
        "Content-Type": "application/json"
      },
      data: {
        "query": searchInputVal,
        "source": (dataSource == "all" ? "scholar" : dataSource)
      }
    }).then((response) => {
      setSearchResults(response.data);
    }).catch((err) => {
      console.log(err);
      setShowRequestError(true);
    }).finally(() => {
      afterSearchTrigger();
      setIsLoading(false);
    });
  };

  const handleDataFileUpload = () => {
    dataFileInput.current.click();
  }

  const handleDataFileChange = (e) => {
    try {
      searchTrigger();
      setSearchBardCollaped(true);
      setShowSearchResults(false);
      setShowUploadSearchResults(false);
      Papa.parse(e.target.files[0], {
        header: true,
        skipEmptyLines: true,
        complete: function (results) {
          setDataFileData(results.data);
        },
      });
      setShowUploadDataSearchResults(true);
    } catch (ex) {
      console.log(ex);
    }
  };

  const handleFileUpload = () => {
    fileInput.current.click();
  };

  const handleFileChange = (e) => {
    try {
      searchTrigger();
      setSearchBardCollaped(true);
      setShowSearchResults(false);
      setShowUploadDataSearchResults(false);
      setPdfFileName(e.target.files[0].name);
      setPdfPath(URL.createObjectURL(e.target.files[0]));
      setShowUploadSearchResults(true);
    }
    catch (ex) {
      console.log(ex);
    }
  };

  const handleCloseRequestError = () => {
    setShowRequestError(false);
  }

  return (
    <>
      <div className={"SearchBarContainer " + (searchStarted ? "collapsed" : "") + (isLoading ? " loading" : "")} >
        <Title className="CompanyLogo">Palooza{searchStarted ? "" : ": Revolutionizing Research with LLM's"}</Title>
        <div className="SearchContainer" style={{ marginTop: searchBarCollapsed ? 10 : 0 }}>
          <Container
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            hover={showSearchInput}
            className="SearchBoxContainer"
          >
            <SearchInput ref={targetRef} showSearchInput={showSearchInput} onChange={handleInputChange} onKeyUp={handleKeyPress} className="CustomSearchInput" />
            {showSearchInput ? <IconRightArrow onClick={handleFormSubmittion} /> : <IconMagnifyingGlass />}

          </Container>
          <Stack direction="row" spacing={2} sx={{ mt: searchBarCollapsed ? 0 : 5 }} className="searchOptions">
            <FormControl size="small" color="grey" sx={{ minWidth: "120px" }}>
              <InputLabel id="datasource-label" sx={{ color: "white" }}>Data Source</InputLabel>
              <Select
                labelId="datasource-label"
                id="datasource"
                value={dataSource}
                label="Data Source"
                onChange={(e) => { setDataSource(e.target.value) }}
                sx={{
                  color: 'white',
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'white !important'
                  },
                  '& .MuiSvgIcon-root': {
                    color: 'white'
                  }
                }}
              >
                <MenuItem value={"all"} selected>All</MenuItem>
                <MenuItem value={"scholar"}>Scholar</MenuItem>
                <MenuItem value={"arxiv"}>Arxiv</MenuItem>
                <MenuItem value={"pubmed"}>Pubmed</MenuItem>
              </Select>
            </FormControl>
            <input
              type="file"
              onChange={(e) => handleDataFileChange(e)}
              ref={dataFileInput}
              style={{ "display": "None" }}
            />
            <Button color="secondary" variant="outlined" startIcon={<UploadFileIcon fontSize="inherit" />} onClick={handleDataFileUpload} size={searchBarCollapsed ? "small" : "medium"} sx={{minWidth: "150px", height: (searchBarCollapsed ? "40px" : "inherit")}}>
              Upload Data
            </Button>

            <input
              type="file"
              onChange={(e) => handleFileChange(e)}
              ref={fileInput}
              style={{ "display": "None" }}
            />
            <Button variant="outlined" color="warning" startIcon={<UploadFileIcon />} onClick={handleFileUpload} size={searchBarCollapsed ? "small" : "medium"} sx={{minWidth: "200px", height: (searchBarCollapsed ? "40px" : "inherit")}}>
              Upload Document
            </Button>
          </Stack>
        </div>
      </div>
      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ m: 3 }}>
        {searchResults && searchResults.related_search && searchResults.related_search.map(related_search_keyword => <Chip label={related_search_keyword} color="primary" variant="outlined" style={{ color: "#fff" }} onClick={() => { performCustomSearch(related_search_keyword) }} />)}
      </Stack>
      {showSearchResults ? <SearchResults isLoading={isLoading} searchInputVal={searchInputVal} searchResults={searchResults} isDataSearch={useDataSearch} isWebSearch={useWebSearch} searchTrend={searchTrend}/> : <></>}
      {showUploadSearchResults ? <UploadSearchResults isLoading={isLoading} pdfPath={pdfPath} pdfFileName={pdfFileName} /> : <></>}
      {showUploadDataSearchResults ? <UploadDataSearchResults dataFileData={dataFileData} /> : <></>}
      <Snackbar anchorOrigin={{ vertical: "top", horizontal: "right" }} open={showRequestError} autoHideDuration={6000} onClose={handleCloseRequestError}>
        <Alert onClose={handleCloseRequestError} severity="error" sx={{ width: '100%' }}>
          Failed to load response
        </Alert>
      </Snackbar>
    </>
  );
}

export default Search;
