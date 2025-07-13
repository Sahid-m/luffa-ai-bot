import {Routes, Route} from 'react-router-dom';
import Home from './pages/home.jsx';
import './App.css';

function App() {
    return (
        <Routes>
            <Route>
                <Route path="/" element={<Home/>}/>
                <Route path="*" element={<div className="p-8 text-center">Page Not Found</div>}/>
            </Route>
        </Routes>
    )
}

export default App;
