import { Outlet, useLocation } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

function AppLayout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-[#070b12] text-white">
      <Navbar />

      <main>
        <div key={location.pathname} className="route-enter">
          <Outlet />
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default AppLayout;
