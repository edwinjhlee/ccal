from datetime import date
import datetime
import cnlunar
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Markdown, Static
from rich.text import Text

# 示例事件数据
EVENTS = {
    date(2025, 6, 1): [
        {"text": "Get visa", "color": "yellow", "icon": "⚑"},
        {"text": "儿童节", "color": "magenta", "icon": "🎈"},
    ],
    date(2025, 6, 5): [
        {"text": "芒种", "color": "green", "icon": "🌱"},
    ],
    date(2025, 6, 14): [
        {"text": "Concert", "color": "magenta", "icon": "🎵"},
    ],
    date(2025, 6, 22): [
        {"text": "端午节", "color": "cyan", "icon": "🥟"},
    ],
}

# 示例 Journal 数据
JOURNAL = [
    {"text": "Prepare for rehearsal", "color": "magenta", "icon": "🎸"},
    {"text": "Get tickets", "color": "yellow", "icon": "⚑", "date": "2025/6/1"},
    {"text": "Write a calendar app", "color": "cyan", "icon": "📝"},
]

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

class KeyCatcher(Static):
    def __init__(self, app_ref: 'CalendarApp'):
        super().__init__("", id="keycatcher")
        self.app_ref = app_ref

    def on_mount(self):
        self.focus()

    async def on_key(self, event):
        print("KEY:", event.key)
        if event.key in ("left", "arrow_left", "h", "a"):
            self.app_ref.action_prev_month()
            event.stop()
        elif event.key in ("right", "arrow_right", "l", "d"):
            self.app_ref.action_next_month()
            event.stop()

class CalendarApp(App):
    CSS_PATH = "calendar.tcss"

    def __init__(self):
        super().__init__()
        today = date.today()
        self.current_date = today
        self.selected_date = today  # 只在此初始化
        self.keycatcher = None

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Vertical(
                Static(self.current_date.strftime("%B %Y"), id="month_label"),
                self.render_calendar(),
                id="calendar_area"
            ),
            Vertical(
                Static("农历信息", id="journal_title"),
                self.render_journal(),
                Static("Journal", id="journal_title2"),
                self.render_journal_events(),
                id="journal_area"
            ),
            id="main_area"
        )
        yield Static("[d] Toggle dark mode   [q] Quit", id="footer")
        self.keycatcher = KeyCatcher(self)
        yield self.keycatcher

    def render_calendar(self):
        # 生成日历网格（极简无边框）
        first_day = self.current_date.replace(day=1)
        start_weekday = (first_day.weekday() + 1) % 7  # 0=Mon
        num_days = (date(self.current_date.year, self.current_date.month + 1, 1) if self.current_date.month < 12 else date(self.current_date.year + 1, 1, 1))
        num_days = (num_days - first_day).days
        days = []
        # 填充空白
        for _ in range(start_weekday):
            days.append(Static(Text(""), classes="calendar-cell"))
        # 填充日期
        for day in range(1, num_days + 1):
            d = date(self.current_date.year, self.current_date.month, day)
            cell_text = Text()
            if d == date.today():
                cell_text.append(f"{day:02d}", style="bold")
            else:
                cell_text.append(f"{day:02d}")
            cell_text.append("\n")
            for idx, event in enumerate(EVENTS.get(d, [])):
                cell_text.append(f"{event['icon']} {event['text']}", style=event['color'])
                if idx < len(EVENTS.get(d, [])) - 1:
                    cell_text.append("\n")
            classes = ["calendar-cell"]
            if d == date.today():
                classes.append("-today")
            if d.weekday() == 5 or d.weekday() == 6:
                classes.append("-weekend")
            days.append(Static(cell_text, classes=" ".join(classes)))
        # 补齐最后一行
        while len(days) % 7 != 0:
            days.append(Static(Text(""), classes="calendar-cell"))
        # 生成表头
        header = Horizontal(*[Static(day, classes="calendar-header") for day in WEEKDAYS])
        # 生成每周一行
        rows = [header]
        for i in range(0, len(days), 7):
            rows.append(Horizontal(*days[i:i+7]))
        return Vertical(*rows, id="calendar_grid")

    def render_journal(self):
        dt = datetime.datetime(self.selected_date.year, self.selected_date.month, self.selected_date.day, 10, 0)
        a = cnlunar.Lunar(dt, godType='8char')
        dic = {
            '日期': a.date,
            '农历': f"{a.lunarYearCn} {a.year8Char}[{a.chineseYearZodiac}]年 {a.lunarMonthCn}{a.lunarDayCn}",
            '星期': a.weekDayCn,
            '今日节日': '、'.join(filter(None, a.get_legalHolidays() + a.get_otherHolidays() + a.get_otherLunarHolidays())) or '无',
            '八字': f"[cyan]{a.year8Char} {a.month8Char} {a.day8Char} {a.twohour8Char}[/cyan]",
            '今日节气': a.todaySolarTerms or '无',
            '下一节气': f"{a.nextSolarTerm or '无'} {a.nextSolarTermDate or ''}",
            '生肖': a.chineseYearZodiac,
            '星座': a.starZodiac,
            '宜': a.goodThing,
            '忌': a.badThing,
        }
        def join_multiline(items, color, per_line=6):
            lines = []
            for i in range(0, len(items), per_line):
                chunk = items[i:i+per_line]
                lines.append(f"[{color}]" + "、".join(chunk) + f"[/{color}]")
            return lines if lines else ["[dim]  无[/dim]"]
        lines = []
        for k, v in dic.items():
            if k == '宜':
                lines.append(f"[b][red]{k}[/red][/b]:")
                lines += join_multiline(v, "red", 6)
            elif k == '忌':
                lines.append(f"[b][grey]{k}[/grey][/b]:")
                lines += join_multiline(v, "grey", 6)
            elif k == '八字':
                lines.append(f"[b]{k}[/b]: {v}")
            else:
                lines.append(f"[b]{k}[/b]: {v}")
        return Static('\n'.join(lines), classes="journal-entry", markup=True)

    def render_journal_events(self):
        items = []
        for entry in JOURNAL:
            line = Text()
            line.append(f"{entry.get('icon','')} ", style=entry.get('color','white'))
            line.append(f"{entry['text']}", style=f"bold {entry.get('color','white')}")
            if entry.get("date"):
                line.append(f" {entry['date']}", style="dim")
            items.append(Static(line, classes="journal-entry"))
        return Vertical(*items, id="journal_list")

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        ("left", "prev_month", "Prev Month"),
        ("arrow_left", "prev_month", "Prev Month"),
        ("right", "next_month", "Next Month"),
        ("arrow_right", "next_month", "Next Month"),
        ("h", "prev_month", "Prev Month"),
        ("a", "prev_month", "Prev Month"),
        ("l", "next_month", "Next Month"),
        ("d", "next_month", "Next Month"),
    ]

    def action_toggle_dark(self):
        pass  # 可根据 textual 版本实现深色切换

    def action_prev_month(self):
        year = self.current_date.year
        month = self.current_date.month - 1
        if month == 0:
            year -= 1
            month = 12
        day = min(self.current_date.day, self._days_in_month(year, month))
        self.current_date = date(year, month, day)
        self.selected_date = self.current_date  # 切换月份时自动选中1号
        self.refresh()

    def action_next_month(self):
        year = self.current_date.year
        month = self.current_date.month + 1
        if month == 13:
            year += 1
            month = 1
        day = min(self.current_date.day, self._days_in_month(year, month))
        self.current_date = date(year, month, day)
        self.selected_date = self.current_date  # 切换月份时自动选中1号
        self.refresh()

    def _days_in_month(self, year, month):
        from calendar import monthrange
        return monthrange(year, month)[1]

    async def on_mount(self):
        self.set_focus(None)

    async def on_key(self, event):
        print("KEY:", event.key)
        if event.key in ("left", "arrow_left", "h", "a"):
            self.action_prev_month()
            event.stop()
        elif event.key in ("right", "arrow_right", "l", "d"):
            self.action_next_month()
            event.stop()

if __name__ == "__main__":
    app = CalendarApp()
    app.run()

def main_entry():
    app = CalendarApp()
    app.run()
