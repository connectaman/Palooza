import React, { useState, useEffect } from 'react';
import Search from '../../Components/Search/Search';
import "./Homepage.css";
import FavoriteIcon from '@mui/icons-material/Favorite';

const Homepage = () => {

    const [searchStarted, setSearchStarted] = useState(false);

    const handleSearchStarted = () => {
      document.body.style.backgroundColor = "#222831";
      setSearchStarted(true);
    }

    const handleSearchFinished = () => {
      document.body.style.backgroundColor = null;
    }

  return (
    <>
      <div className={"App " + (searchStarted ? "" : "DisplayCenter")}>
        <Search searchStarted={searchStarted} searchTrigger={handleSearchStarted} afterSearchTrigger={handleSearchFinished} />
      </div>
      <div className="AppFooter">
        Made with <FavoriteIcon color="error" sx={{m: 1}}/> by Aman Ulla and Srinivas Alva.
      </div>
    </>
    
  )
}

export default Homepage;
