{pkgs}: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pandas
    pkgs.python310Packages.plotly
    pkgs.python310Packages.streamlit
  ];
}