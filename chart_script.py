import plotly.graph_objects as go
import plotly.io as pio

# Create figure
fig = go.Figure()

# Set up coordinate system
fig.add_trace(go.Scatter(
    x=[0, 500],
    y=[0, 350],
    mode='markers',
    marker=dict(size=0, opacity=0),
    showlegend=False
))

# Color mapping
colors = {
    "source": "#1FB8CD",
    "vpc": "#ECEBD5", 
    "subnet_public": "#FFC185",
    "subnet_private": "#5D878F",
    "database": "#D2BA4C",
    "application": "#B4413C",
    "migration": "#964325",
    "security": "#944454"
}

shapes = []
annotations = []

# AWS VPC Container (large background)
shapes.append(dict(
    type="rect",
    x0=180, y0=50,
    x1=480, y1=320,
    fillcolor=colors["vpc"],
    line=dict(color="black", width=3),
    opacity=0.3
))
annotations.append(dict(
    x=190, y=310,
    text="AWS VPC",
    showarrow=False,
    font=dict(size=14, color="black"),
    align="left"
))

# Availability Zone 1 (left side of VPC)
shapes.append(dict(
    type="rect",
    x0=190, y0=60,
    x1=330, y1=300,
    fillcolor="lightgray",
    line=dict(color="gray", width=1, dash="dash"),
    opacity=0.2
))
annotations.append(dict(
    x=200, y=290,
    text="AZ-1",
    showarrow=False,
    font=dict(size=12, color="gray"),
    align="left"
))

# Availability Zone 2 (right side of VPC)
shapes.append(dict(
    type="rect",
    x0=340, y0=60,
    x1=470, y1=300,
    fillcolor="lightgray",
    line=dict(color="gray", width=1, dash="dash"),
    opacity=0.2
))
annotations.append(dict(
    x=350, y=290,
    text="AZ-2",
    showarrow=False,
    font=dict(size=12, color="gray"),
    align="left"
))

# Public Subnet (top of each AZ)
shapes.append(dict(
    type="rect",
    x0=200, y0=230,
    x1=320, y1=280,
    fillcolor=colors["subnet_public"],
    line=dict(color="orange", width=2),
    opacity=0.6
))
annotations.append(dict(
    x=210, y=270,
    text="Public Subnet",
    showarrow=False,
    font=dict(size=10, color="black"),
    align="left"
))

shapes.append(dict(
    type="rect",
    x0=350, y0=230,
    x1=460, y1=280,
    fillcolor=colors["subnet_public"],
    line=dict(color="orange", width=2),
    opacity=0.6
))
annotations.append(dict(
    x=360, y=270,
    text="Public Subnet",
    showarrow=False,
    font=dict(size=10, color="black"),
    align="left"
))

# Private Subnet AZ-1 (bottom of AZ-1)
shapes.append(dict(
    type="rect",
    x0=200, y0=80,
    x1=320, y1=180,
    fillcolor=colors["subnet_private"],
    line=dict(color="darkblue", width=2),
    opacity=0.6
))
annotations.append(dict(
    x=210, y=170,
    text="Private Subnet",
    showarrow=False,
    font=dict(size=10, color="white"),
    align="left"
))

# Private Subnet AZ-2 (bottom of AZ-2)
shapes.append(dict(
    type="rect",
    x0=350, y0=80,
    x1=460, y1=180,
    fillcolor=colors["subnet_private"],
    line=dict(color="darkblue", width=2),
    opacity=0.6
))
annotations.append(dict(
    x=360, y=170,
    text="Private Subnet",
    showarrow=False,
    font=dict(size=10, color="white"),
    align="left"
))

# Supabase (source - outside AWS)
shapes.append(dict(
    type="rect",
    x0=30, y0=150,
    x1=130, y1=200,
    fillcolor=colors["source"],
    line=dict(color="black", width=2),
    opacity=0.8
))
annotations.append(dict(
    x=80, y=175,
    text="Supabase<br>PostgreSQL",
    showarrow=False,
    font=dict(size=12, color="black"),
    align="center"
))

# Load Balancer (in public subnet)
shapes.append(dict(
    type="rect",
    x0=220, y0=240,
    x1=300, y1=270,
    fillcolor=colors["application"],
    line=dict(color="black", width=2),
    opacity=0.8
))
annotations.append(dict(
    x=260, y=255,
    text="Load Balancer",
    showarrow=False,
    font=dict(size=11, color="white"),
    align="center"
))

# Node.js App (in public subnet AZ-2)
shapes.append(dict(
    type="rect",
    x0=370, y0=240,
    x1=440, y1=270,
    fillcolor=colors["application"],
    line=dict(color="black", width=2),
    opacity=0.8
))
annotations.append(dict(
    x=405, y=255,
    text="Node.js App",
    showarrow=False,
    font=dict(size=11, color="white"),
    align="center"
))

# Primary RDS (in private subnet AZ-1)
shapes.append(dict(
    type="rect",
    x0=220, y0=110,
    x1=300, y1=150,
    fillcolor=colors["database"],
    line=dict(color="black", width=2),
    opacity=0.8
))
annotations.append(dict(
    x=260, y=130,
    text="Primary RDS<br>PostgreSQL",
    showarrow=False,
    font=dict(size=11, color="black"),
    align="center"
))

# Read Replica (in private subnet AZ-2)
shapes.append(dict(
    type="rect",
    x0=370, y0=110,
    x1=440, y1=150,
    fillcolor=colors["database"],
    line=dict(color="black", width=2),
    opacity=0.8
))
annotations.append(dict(
    x=405, y=130,
    text="Read Replica<br>PostgreSQL",
    showarrow=False,
    font=dict(size=11, color="black"),
    align="center"
))

# Security Groups (represented as dotted circles around databases)
shapes.append(dict(
    type="circle",
    x0=210, y0=100,
    x1=310, y1=160,
    fillcolor=colors["security"],
    line=dict(color=colors["security"], width=3, dash="dot"),
    opacity=0.1
))
shapes.append(dict(
    type="circle",
    x0=360, y0=100,
    x1=450, y1=160,
    fillcolor=colors["security"],
    line=dict(color=colors["security"], width=3, dash="dot"),
    opacity=0.1
))

# Security Group labels
annotations.append(dict(
    x=260, y=95,
    text="Security Group",
    showarrow=False,
    font=dict(size=8, color=colors["security"]),
    align="center"
))
annotations.append(dict(
    x=405, y=95,
    text="Security Group",
    showarrow=False,
    font=dict(size=8, color=colors["security"]),
    align="center"
))

# Migration process indicator
shapes.append(dict(
    type="rect",
    x0=140, y0=160,
    x1=170, y1=190,
    fillcolor=colors["migration"],
    line=dict(color="black", width=2),
    opacity=0.8
))
annotations.append(dict(
    x=155, y=175,
    text="pg_dump/<br>restore",
    showarrow=False,
    font=dict(size=9, color="white"),
    align="center"
))

# Connection arrows with labels
# Migration arrow (Supabase to Primary RDS)
annotations.append(dict(
    x=220, y=130,
    ax=130, ay=175,
    xref="x", yref="y",
    axref="x", ayref="y",
    showarrow=True,
    arrowhead=3,
    arrowsize=2,
    arrowwidth=4,
    arrowcolor="#B4413C",
    text="Migration",
    font=dict(size=10, color="white"),
    bgcolor="#B4413C",
    bordercolor="#B4413C",
    borderwidth=1
))

# Replication arrow (Primary to Replica)
annotations.append(dict(
    x=370, y=130,
    ax=300, ay=130,
    xref="x", yref="y",
    axref="x", ayref="y",
    showarrow=True,
    arrowhead=3,
    arrowsize=2,
    arrowwidth=3,
    arrowcolor="#964325",
    text="Replication",
    font=dict(size=10, color="white"),
    bgcolor="#964325",
    bordercolor="#964325",
    borderwidth=1
))

# Write operations (App to Primary)
annotations.append(dict(
    x=280, y=150,
    ax=380, ay=240,
    xref="x", yref="y",
    axref="x", ayref="y",
    showarrow=True,
    arrowhead=3,
    arrowsize=1.5,
    arrowwidth=3,
    arrowcolor="#944454",
    text="Write Ops",
    font=dict(size=9, color="white"),
    bgcolor="#944454",
    bordercolor="#944454",
    borderwidth=1
))

# Read operations (App to Replica)
annotations.append(dict(
    x=405, y=150,
    ax=405, ay=240,
    xref="x", yref="y",
    axref="x", ayref="y",
    showarrow=True,
    arrowhead=3,
    arrowsize=1.5,
    arrowwidth=3,
    arrowcolor="#13343B",
    text="Read Ops",
    font=dict(size=9, color="white"),
    bgcolor="#13343B",
    bordercolor="#13343B",
    borderwidth=1
))

# Load balancer to app connection
annotations.append(dict(
    x=370, y=255,
    ax=300, ay=255,
    xref="x", yref="y",
    axref="x", ayref="y",
    showarrow=True,
    arrowhead=2,
    arrowsize=1.5,
    arrowwidth=2,
    arrowcolor="gray",
    text="Traffic",
    font=dict(size=8, color="white"),
    bgcolor="gray",
    bordercolor="gray",
    borderwidth=1
))

# Update layout
fig.update_layout(
    title="Supabase to AWS RDS Migration",
    shapes=shapes,
    annotations=annotations,
    xaxis=dict(
        range=[0, 500],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        title=""
    ),
    yaxis=dict(
        range=[0, 350],
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        title=""
    ),
    plot_bgcolor="white",
    showlegend=False
)

# Save the chart
fig.write_image("architecture_diagram.png")