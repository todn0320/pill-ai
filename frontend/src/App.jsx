import { Route, Routes } from "react-router-dom";
import "./App.css";
import Main from "./pill_ai/main.jsx";
import LandingPage from "./pill_ai/pages/landing/LandingPage.jsx";
import HomePage from "./pill_ai/pages/home/HomePage.jsx";
import SearchPage from "./pill_ai/pages/search/SearchPage.jsx";
import CheckPage from "./pill_ai/pages/check/CheckPage.jsx";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<Main />}>
          <Route index element={<HomePage />} />
          <Route path="home" element={<HomePage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="check" element={<CheckPage />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
