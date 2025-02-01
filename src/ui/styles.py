LIGHT_STYLE = """
QMainWindow {
    background-color: #ffffff;
}
QTabWidget::pane {
    border: 1px solid #cccccc;
    background-color: #ffffff;
}
QTabBar::tab {
    background-color: #f0f0f0;
    padding: 8px 20px;
    margin: 2px;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-bottom: none;
}
"""

DARK_STYLE = """
QMainWindow {
    background-color: #2b2b2b;
}
QTabWidget::pane {
    border: 1px solid #3d3d3d;
    background-color: #2b2b2b;
}
QTabBar::tab {
    background-color: #353535;
    color: #ffffff;
    padding: 8px 20px;
    margin: 2px;
}
QTabBar::tab:selected {
    background-color: #2b2b2b;
    border: 1px solid #3d3d3d;
    border-bottom: none;
}
"""
