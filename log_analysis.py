import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess
from datetime import datetime, timedelta

SECURITY_EVENT_LABELS = {
    4624: "Successful Logon",
    4625: "Failed Logon",
    4634: "Logoff",
    4648: "Explicit Credential Logon",
    4672: "Special Privileges Assigned",
    4720: "User Account Created",
    4726: "User Account Deleted",
    4740: "Account Locked Out",
    4771: "Kerberos Pre-Auth Failed",
    }

def export_logs():
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    commands = [
        f'Get-WinEvent -FilterHashtable @{{LogName="Security"; StartTime="{one_week_ago}"}} | Export-Csv security_logs.csv -NoTypeInformation',
        f'Get-WinEvent -FilterHashtable @{{LogName="System";   StartTime="{one_week_ago}"}} | Export-Csv system_logs.csv   -NoTypeInformation',
    ]
    for cmd in commands:
        subprocess.run(["powershell", "-Command", cmd], check=True)
    print("[Ok] Logs exported from Windows Event Viewer")

def load_log(filename):
    df = pd.read_csv(filename, dtype=str)
    df = df[["LevelDisplayName", "TimeCreated", "ProviderName", "Id", "TaskDisplayName", "Message"]]

    rename = {
        "TimeCreated": "Date and Time",
        "LevelDisplayName": "Level",
        "ProviderName": "Source",
        "Id": "Event ID",
        "TaskDisplayName": "Task Category",
        "Message": "Description",
    }
    df.rename(columns={k: v for k, v in rename.items() if k in df.columns}, inplace=True)

    df["Date and Time"] = pd.to_datetime(df["Date and Time"], errors="coerce")
    df["Event ID"] = pd.to_numeric(df.get("Event ID", pd.Series(dtype=str)), errors="coerce").astype("Int64")
    df["Level"] = df.get("Level", pd.Series(dtype=str)).fillna("Unknown").str.strip()
        
    return df

def parse_security(df):
    df = df.copy()
    df["event_label"] = df["Event ID"].map(SECURITY_EVENT_LABELS).fillna("Other")
    return df

# CHART 1: Bar chart — event levels (errors)
def chart_event_levels(df):
    counts = df["Level"].value_counts()
    ax = counts.plot(kind="bar")
    ax.bar_label(ax.containers[0])
    plt.title("Event frequency by Level")
    plt.xlabel("Level")
    plt.ylabel("Count")
    plt.savefig("chart1_event_levels.png")
    #plt.show()
    plt.close()

# CHART 2: Pie chart — event level distribution
def chart_level_pie(df):
    counts = df["Level"].value_counts()
    counts.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Event level distribution")
    plt.ylabel("")
    plt.savefig("chart2_level_pie.png")
    #plt.show()
    plt.close()

# CHART 3: Time series — events over time
def chart_events_over_time(df):
    hourly = df.groupby(df["Date and Time"].dt.floor("h")).size()
    hourly.plot()
    plt.title("Events per hour")
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.savefig("chart3_events_over_time.png")
    #plt.show()
    plt.close()

# CHART 4: Time series — login activity

def chart_login_times(df):
    logon_df = df[df["Event ID"] == 4624]
    if logon_df.empty:
        print("[Not Ok] No successful logon events (4624) found.")
        return
    hourly = logon_df.groupby(logon_df["Date and Time"].dt.floor("h")).size()
    hourly.plot()
    plt.title("User login times (Logons per hour)")
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.savefig("chart4_login_times.png")
    #plt.show()
    plt.close()

# CHART 5: Bar chart — successful vs failed logins

def chart_login_comparison(df):
    login_df = df[df["Event ID"].isin([4624, 4625])].copy()
    if login_df.empty:
        print("[Not Ok] No login events (4624/4625) found.")
        return
    login_df["event_label"] = login_df["Event ID"].map(SECURITY_EVENT_LABELS)
    counts = login_df["event_label"].value_counts()
    ax = counts.plot(kind="bar")
    ax.bar_label(ax.containers[0])
    plt.title("Successful vs failed logons")
    plt.xlabel("Type")
    plt.ylabel("Count")
    plt.savefig("chart5_login_comparison.png")
    #plt.show()
    plt.close()


def export_html(sys_df, sec_df):
    html = f"""
    <html>
    <body>
        <h1>Windows log analysis report</h1>
        <h2>System log summary</h2>
        <p>Total events: {len(sys_df)}</p>
        <p>Start date: {sys_df['Date and Time'].min()}</p>
        <p>End date: {sys_df['Date and Time'].max()}</p>
        <pre>Event levels:\n{sys_df['Level'].value_counts().rename_axis(None).to_string()}</pre>

        <h2>Security log summary</h2>
        <p>Total events: {len(sec_df)}</p>
        <p>Start date: {sec_df['Date and Time'].min()}</p>
        <p>End date: {sec_df['Date and Time'].max()}</p>
        <pre>Event levels:\n{sec_df['Level'].value_counts().rename_axis(None).to_string()}</pre>
        <pre>Top Event IDs:\n{sec_df['Event ID'].value_counts().rename_axis(None).head(5).to_string()}</pre>


        <h2>Event frequency by level</h2>
        <img src="chart1_event_levels.png">  

        <h2>Event level distribution</h2>
        <img src="chart2_level_pie.png">  

        <h2>Events per hour</h2>
        <img src="chart3_events_over_time.png">  

        <h2>User login times</h2>
        <img src="chart4_login_times.png">  

        <h2>Successful vs failed logons</h2>
        <img src="chart5_login_comparison.png">  

    </body>
    </html>
    """
    with open("report.html", "w") as f:
        f.write(html)
    print("report.html saved")


export_logs()

print("\n" + "*" * 80)
print(f"\nSystem log information: {'system_logs.csv'}")
sys_df = load_log("system_logs.csv")
print(f"\nTotal events : {len(sys_df)}")
print(f"\nStart date   : {sys_df['Date and Time'].min()}")
print(f"End date   : {sys_df['Date and Time'].max()}")
print(f"\nEvent levels :\n{sys_df['Level'].value_counts().rename_axis(None).to_string()}")

print("\n" + "*" * 80)
print(f"\nSecurity log information: {'security_logs.csv'}")
sec_df = parse_security(load_log("security_logs.csv"))
print(f"\nTotal events : {len(sec_df)}")
print(f"\nStart date   : {sec_df['Date and Time'].min()}")
print(f"End date   : {sec_df['Date and Time'].max()}")
print(f"\nEvent levels :\n{sec_df['Level'].value_counts().rename_axis(None).to_string()}")
print(f"\nTop Event IDs:\n{sec_df['Event ID'].value_counts().rename_axis(None).head(5).to_string()}")

print("\n" + "*" * 80)
chart_event_levels(sys_df)
chart_level_pie(sys_df)
chart_events_over_time(sys_df)
chart_login_times(sec_df)
chart_login_comparison(sec_df)

export_html(sys_df, sec_df)
