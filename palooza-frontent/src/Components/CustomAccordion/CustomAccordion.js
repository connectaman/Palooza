import React, { useState } from 'react';
import { styled } from '@mui/material/styles';
import ArrowForwardIosSharpIcon from '@mui/icons-material/ArrowForwardIosSharp';
import MuiAccordion from '@mui/material/Accordion';
import MuiAccordionSummary from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';

const Accordion = styled((props) => (
    <MuiAccordion disableGutters elevation={0} square {...props} />
))(({ theme }) => ({
    border: `1px solid ${theme.palette.divider}`,
    '&:not(:last-child)': {
        borderBottom: 0,
    },
    '&:before': {
        display: 'none',
    },
}));

const AccordionSummary = styled((props) => (
    <MuiAccordionSummary
        expandIcon={props.alwaysCollapsed ? <></> : <ArrowForwardIosSharpIcon sx={{ fontSize: '0.9rem' }} />}
        {...props}
    />
))(({ theme }) => ({
    backgroundColor:
        theme.palette.mode === 'dark'
            ? 'rgba(255, 255, 255, .05)'
            : 'rgba(0, 0, 0, .03)',
    flexDirection: 'row-reverse',
    '& .MuiAccordionSummary-expandIconWrapper.Mui-expanded': {
        transform: 'rotate(90deg)',
    },
    '& .MuiAccordionSummary-content': {
        marginLeft: theme.spacing(1),
    },
}));

const AccordionDetails = styled(MuiAccordionDetails)(({ theme }) => ({
    padding: theme.spacing(2),
    borderTop: '1px solid rgba(0, 0, 0, .125)',
}));


function CustomAccordion({ header, body, alwaysCollapsed = false }) {
    const [expanded, setExpanded] = useState(alwaysCollapsed);

    const handleChange = () => {
        if (!alwaysCollapsed) {
            setExpanded(!expanded);
        }
    };

    return (
        <Accordion expanded={expanded} onChange={handleChange} sx={{mt: alwaysCollapsed ? 5 : 0}}>
            <AccordionSummary alwaysCollapsed={alwaysCollapsed}>
                <Typography>{header}</Typography>
            </AccordionSummary>
            <AccordionDetails>
                <Typography style={{textAlign: "left"}}>
                    {body}
                </Typography>
            </AccordionDetails>
        </Accordion>
    )
}

export default CustomAccordion;