import React from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import "./main.css";

const Main = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <div className="app-wrap">
      <div className="app">
        <nav className="sidebar">
          <div className="logo">
            <div className="logo-icon"></div>
            <span className="logo-text">MediLink</span>
          </div>
          <div className="nav">
            <div className="nav-label">메인</div>
            <div className={`nav-item ${isActive("/app") || isActive("/app/home") ? "active" : ""}`} onClick={() => navigate("/app/home")}>
              <div className="nav-dot"></div>홈
            </div>
            <div className={`nav-item ${isActive("/app/search") ? "active" : ""}`} onClick={() => navigate("/app/search")}>
              <div className="nav-dot"></div>검색
            </div>
            <div className="nav-item">
              <div className="nav-dot"></div>내 약함
            </div>
            <div className={`nav-item ${isActive("/app/check") ? "active" : ""}`} onClick={() => navigate("/app/check")}>
              <div className="nav-dot"></div>병용 확인
            </div>
            <div className="nav-label">알림</div>
            <div className="nav-item">
              <div className="nav-dot"></div>알림
              <span className="nav-badge">1</span>
            </div>
            <div className="nav-label">기타</div>
            <div className="nav-item">
              <div className="nav-dot"></div>의료진 공유
            </div>
            <div className="nav-item">
              <div className="nav-dot"></div>설정
            </div>
          </div>
          <div className="sidebar-footer">
            <div className="avatar">민지</div>
            <div>
              <div className="user-name">김민지</div>
              <div className="user-role">일반 사용자</div>
            </div>
          </div>
        </nav>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Main;
