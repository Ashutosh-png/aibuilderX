import logo from './logo.svg';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import ComicGenerator from './components/ComicGenerator';
import ReactGa from "react-ga";
import { useEffect } from 'react';


ReactGa.initialize("G-KFK5ZTGNZZ");
function App() {
  useEffect(()=>{
    ReactGa.pageview(window.location.pathname + window.location.search);
  });
  return (
   <>
    <Router>
        <Routes>
        <Route path="/" exact element={<HomePage />} />
        <Route path="/ComicGenerator" element={<ComicGenerator/>}/>
        </Routes>
   </Router>
   
   </>
  );
}

export default   App;
