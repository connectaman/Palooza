import React, { useEffect, useState } from 'react';
import Tree from 'react-d3-tree';
import "./CustomMindmap.css";

function CustomMindmap({ mindmap }) {
    return (
        <div id="treeWrapper" style={{ width: '100%', height: '100vh' }}>
            {mindmap ? <Tree data={mindmap} nodeSize={{ x: 600, y: 300 }}/> : <></>}
        </div>
    )
}

export default CustomMindmap