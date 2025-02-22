import { Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import SignInPage from "./pages/SignIn";
import SignUpPage from "./pages/SignUp";
import LandingPage from "./pages/LandingPage";
import VideoCall from "./pages/VideoCall";
import VideoReview from "./pages/VideoReview";
import Dashboard from "./pages/Dashboard";
import WorkflowPage from "./pages/WorkflowPage";
import Documents from "./pages/Documents";
import Mail from "./pages/Mail";
const App = () => {
    return (
        <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/sign-in" element={<SignInPage />} />
            <Route path="/sign-up" element={<SignUpPage />} />

            {/* Private Nested Routes */}
            <Route path="/" element={<AppLayout />}>
                <Route path="/dashboard" element={<Dashboard/>} />
                <Route path="/videocall" element={<VideoCall/>} />
                <Route path="/videoreview" element={<VideoReview/>} />
                <Route path="/workflow" element={<WorkflowPage/>} />
                <Route path="/documents" element={<Documents/>} />
                <Route path="/mail" element={<Mail/>} />

            </Route>
        </Routes>
    );
};

export default App;
