"""
Reports & Analytics Module
==========================
Generates charts and statistics using Matplotlib.
Charts are returned as base64-encoded PNG strings.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter
from datetime import datetime, timedelta

COLORS = ['#6C63FF', '#FF6584', '#43E97B', '#F9A826', '#00D2FF',
          '#A855F7', '#EC4899', '#14B8A6', '#F97316', '#3B82F6']


def _fig_to_base64(fig):
    """Convert a Matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def generate_category_chart(lost_items, found_items):
    """Bar chart comparing lost vs found items by category."""
    lost_cats = Counter(i['category'] for i in lost_items)
    found_cats = Counter(i['category'] for i in found_items)
    all_cats = sorted(set(list(lost_cats.keys()) + list(found_cats.keys())))
    if not all_cats:
        all_cats = ['No Data']
    lost_c = [lost_cats.get(c, 0) for c in all_cats]
    found_c = [found_cats.get(c, 0) for c in all_cats]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    x = range(len(all_cats))
    w = 0.35
    ax.bar([i - w/2 for i in x], lost_c, w, label='Lost', color='#FF6584', alpha=0.85)
    ax.bar([i + w/2 for i in x], found_c, w, label='Found', color='#43E97B', alpha=0.85)
    ax.set_xlabel('Category', color='white')
    ax.set_ylabel('Count', color='white')
    ax.set_title('Items by Category', color='white', fontweight='bold')
    ax.set_xticks(list(x))
    ax.set_xticklabels(all_cats, rotation=45, ha='right', color='white', fontsize=9)
    ax.tick_params(axis='y', colors='white')
    ax.legend(facecolor='#16213e', edgecolor='#6C63FF', labelcolor='white')
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('#6C63FF')
    ax.grid(axis='y', alpha=0.2, color='white')
    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_monthly_chart(lost_items, found_items):
    """Line chart showing monthly report trends (last 6 months)."""
    def count_by_month(items, date_field):
        monthly = Counter()
        for item in items:
            ds = item.get(date_field, item.get('created_at', ''))
            if ds:
                try:
                    dt = datetime.strptime(str(ds)[:10], '%Y-%m-%d')
                    monthly[dt.strftime('%Y-%m')] += 1
                except (ValueError, TypeError):
                    pass
        return monthly

    lost_m = count_by_month(lost_items, 'date_lost')
    found_m = count_by_month(found_items, 'date_found')
    months = []
    now = datetime.now()
    for i in range(5, -1, -1):
        dt = now - timedelta(days=30 * i)
        months.append(dt.strftime('%Y-%m'))
    lc = [lost_m.get(m, 0) for m in months]
    fc = [found_m.get(m, 0) for m in months]
    labels = [datetime.strptime(m, '%Y-%m').strftime('%b %Y') for m in months]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    ax.plot(labels, lc, 'o-', color='#FF6584', linewidth=2.5, markersize=8, label='Lost')
    ax.plot(labels, fc, 's-', color='#43E97B', linewidth=2.5, markersize=8, label='Found')
    ax.fill_between(labels, lc, alpha=0.1, color='#FF6584')
    ax.fill_between(labels, fc, alpha=0.1, color='#43E97B')
    ax.set_title('Monthly Trends', color='white', fontweight='bold')
    ax.tick_params(colors='white')
    ax.legend(facecolor='#16213e', edgecolor='#6C63FF', labelcolor='white')
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('#6C63FF')
    ax.grid(alpha=0.2, color='white')
    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_status_pie(lost_items, found_items):
    """Donut chart showing status distribution."""
    all_items = lost_items + found_items
    sc = Counter(i.get('status', 'open') for i in all_items)
    labels = [s.title() for s in sc.keys()] if sc else ['No Data']
    sizes = list(sc.values()) if sc else [1]

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', startangle=90,
        colors=COLORS[:len(labels)], pctdistance=0.80,
        wedgeprops=dict(width=0.4, edgecolor='#1a1a2e', linewidth=2))
    for t in texts:
        t.set_color('white')
    for t in autotexts:
        t.set_color('white')
        t.set_fontweight('bold')
    ax.set_title('Status Distribution', color='white', fontweight='bold', pad=20)
    plt.tight_layout()
    return _fig_to_base64(fig)


def generate_recovery_chart(lost_items):
    """Gauge-style donut showing recovery rate percentage."""
    total = len(lost_items)
    recovered = sum(1 for i in lost_items if i.get('status') == 'recovered')
    rate = (recovered / total * 100) if total > 0 else 0

    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    ax.pie([rate, 100 - rate], startangle=90, colors=['#43E97B', '#2a2a4a'],
           wedgeprops=dict(width=0.3, edgecolor='#1a1a2e', linewidth=2))
    ax.text(0, 0, f'{rate:.1f}%', ha='center', va='center',
            fontsize=36, fontweight='bold', color='#43E97B')
    ax.text(0, -0.15, 'Recovery Rate', ha='center', va='center',
            fontsize=12, color='white', alpha=0.8)
    ax.set_title(f'{recovered} of {total} Recovered', color='white', fontweight='bold', pad=20)
    plt.tight_layout()
    return _fig_to_base64(fig)


def get_statistics(lost_items, found_items):
    """Calculate summary statistics."""
    total_lost = len(lost_items)
    total_found = len(found_items)
    recovered = sum(1 for i in lost_items if i.get('status') == 'recovered')
    open_lost = sum(1 for i in lost_items if i.get('status') == 'open')
    open_found = sum(1 for i in found_items if i.get('status') == 'open')
    now = datetime.now()
    old = 0
    for item in lost_items + found_items:
        if item.get('status') == 'open':
            try:
                dt = datetime.strptime(str(item.get('created_at', ''))[:19], '%Y-%m-%d %H:%M:%S')
                if (now - dt).days > 30:
                    old += 1
            except (ValueError, TypeError):
                pass
    rate = (recovered / total_lost * 100) if total_lost > 0 else 0
    return {
        'total_lost': total_lost, 'total_found': total_found,
        'total_reports': total_lost + total_found, 'recovered': recovered,
        'open_lost': open_lost, 'open_found': open_found,
        'open_cases': open_lost + open_found,
        'recovery_rate': round(rate, 1), 'old_unresolved': old,
    }
