import flet as ft
import re
import sqlite3

def main(page: ft.Page):
    page.title = "Connect Shop"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window_width = 400
    page.window_height = 700

    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY,
        name TEXT,
        phone TEXT UNIQUE
    )
    ''')
    conn.commit()

    def is_valid_egyptian_phone(phone):
        pattern = r'^01[0125][0-9]{8}$'
        return re.match(pattern, phone) is not None

    def is_valid_amount(amount):
        return amount.isdigit()

    def on_phone_change(e):
        phone = phone_input.value
        if len(phone) >= 3:
            cursor.execute("SELECT name, phone FROM contacts WHERE phone LIKE ?", (f"{phone}%",))
            results = cursor.fetchall()
            if results:
                suggestion_dropdown.options = [ft.dropdown.Option(f"{name} - {phone}") for name, phone in results]
                suggestion_dropdown.visible = True
            else:
                suggestion_dropdown.visible = False
        else:
            suggestion_dropdown.visible = False
        page.update()

    phone_input = ft.TextField(
        label="رقم الهاتف",
        text_align=ft.TextAlign.RIGHT,
        on_change=on_phone_change,
        border_color=ft.colors.BLUE_400,
        focused_border_color=ft.colors.BLUE_700,
        border_radius=10
    )
    confirm_phone_input = ft.TextField(
        label="تأكيد رقم الهاتف",
        text_align=ft.TextAlign.RIGHT,
        border_color=ft.colors.BLUE_400,
        focused_border_color=ft.colors.BLUE_700,
        border_radius=10
    )
    amount_input = ft.TextField(
        label="المبلغ",
        text_align=ft.TextAlign.RIGHT,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=ft.colors.BLUE_400,
        focused_border_color=ft.colors.BLUE_700,
        border_radius=10
    )

    suggestion_dropdown = ft.Dropdown(
        width=400,
        options=[],
        visible=False,
        on_change=lambda e: fill_phone_input(e.data)
    )

    verify_button = ft.ElevatedButton("تحقق", on_click=lambda _: verify_inputs(), style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.BLUE_700))
    clear_button = ft.ElevatedButton("مسح", on_click=lambda _: clear_inputs(), style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.RED_700))
    add_name_button = ft.ElevatedButton("إضافة اسم", on_click=lambda _: open_add_name_dialog(), style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.GREEN_700))
    name_list_button = ft.ElevatedButton("قائمة الأسماء", on_click=lambda _: open_name_list(), style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.ORANGE_700))

    action_row1 = ft.Row([verify_button, clear_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    action_row2 = ft.Row([add_name_button, name_list_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    call_button = ft.ElevatedButton("اتصال", on_click=lambda _: make_call(), style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.BLUE_700))
    copy_code_button = ft.ElevatedButton("نسخ الكود", on_click=lambda _: copy_code(), style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.GREEN_700))
    edit_button = ft.ElevatedButton("التعديل", on_click=lambda _: edit_contact(), style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.ORANGE_700))
    delete_button = ft.ElevatedButton("مسح الرقم", on_click=lambda _: delete_contact(), style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.RED_700))

    def verify_inputs():
        phone = phone_input.value
        confirm_phone = confirm_phone_input.value
        amount = amount_input.value
        if not is_valid_egyptian_phone(phone):
            page.snack_bar = ft.SnackBar(ft.Text("رقم الهاتف غير صحيح"), open=True)
        elif phone != confirm_phone:
            page.snack_bar = ft.SnackBar(ft.Text("رقم الهاتف وتأكيد رقم الهاتف غير متطابقين"), open=True)
        elif not is_valid_amount(amount):
            page.snack_bar = ft.SnackBar(ft.Text("المبلغ غير صحيح"), open=True)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("تم التحقق بنجاح"), open=True)
        page.update()

    def clear_inputs():
        phone_input.value = ""
        confirm_phone_input.value = ""
        amount_input.value = ""
        suggestion_dropdown.visible = False
        page.update()

    def open_add_name_dialog():
        def save_name(e):
            if name_input.value and phone_input.value:
                if not is_valid_egyptian_phone(phone_input.value):
                    page.show_snack_bar(ft.SnackBar(content=ft.Text("رقم الهاتف غير صحيح")))
                    return
                try:
                    cursor.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)",
                                   (name_input.value, phone_input.value))
                    conn.commit()
                    page.show_snack_bar(ft.SnackBar(content=ft.Text("تم حفظ جهة الاتصال")))
                    page.dialog.open = False
                    page.update()
                except sqlite3.IntegrityError:
                    page.show_snack_bar(ft.SnackBar(content=ft.Text("رقم الهاتف موجود بالفعل")))
            else:
                page.show_snack_bar(ft.SnackBar(content=ft.Text("يرجى إدخال الاسم ورقم الهاتف")))

        name_input = ft.TextField(label="الاسم")
        phone_input = ft.TextField(label="رقم الهاتف", hint_text="01xxxxxxxxx")
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("إضافة جهة اتصال جديدة"),
            content=ft.Column([name_input, phone_input], tight=True),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda _: close_dlg()),
                ft.TextButton("حفظ", on_click=save_name),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()
        
    def close_dlg():
        page.dialog.open = False
        page.update()    

    def open_name_list():
        def on_select(e):
            selected_name = e.control.data
            cursor.execute("SELECT phone FROM contacts WHERE name = ?", (selected_name,))
            result = cursor.fetchone()
            if result:
                phone_input.value = result[0]
                confirm_phone_input.value = result[0]
                page.dialog.open = False
                page.update()

        cursor.execute("SELECT name FROM contacts")
        names = [row[0] for row in cursor.fetchall()]
        
        name_list = ft.ListView(
            expand=1,
            spacing=10,
            padding=20,
            controls=[
                ft.Card(
                    content=ft.Container(
                        content=ft.Text(name, size=16),
                        padding=10,
                        on_click=on_select,
                        data=name
                    )
                ) for name in names
            ]
        )

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("قائمة الأسماء"),
            content=ft.Container(
                content=name_list,
                height=400,
                width=300
            ),
            actions=[
                ft.TextButton("إغلاق", on_click=lambda _: close_dlg()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def fill_phone_input(data):
        name, phone = data.split(" - ")
        phone_input.value = phone
        confirm_phone_input.value = phone
        suggestion_dropdown.visible = False
        page.update()

    def make_call():
        code = f"*9*7*{phone_input.value}*{amount_input.value}%23"
        page.launch_url(f"tel:{code}")

    def copy_code():
        code = f"*9*7*{phone_input.value}*{amount_input.value}#"
        page.set_clipboard(code)
        page.show_snack_bar(ft.SnackBar(content=ft.Text("تم نسخ الكود")))

    def edit_contact():
        cursor.execute("SELECT name FROM contacts WHERE phone = ?", (phone_input.value,))
        result = cursor.fetchone()
        if result:
            name = result[0]
            def save_edit(e):
                if new_name_input.value and new_phone_input.value:
                    if not is_valid_egyptian_phone(new_phone_input.value):
                        page.show_snack_bar(ft.SnackBar(content=ft.Text("رقم الهاتف الجديد غير صحيح")))
                        return
                    cursor.execute("UPDATE contacts SET name = ?, phone = ? WHERE phone = ?",
                                   (new_name_input.value, new_phone_input.value, phone_input.value))
                    conn.commit()
                    phone_input.value = new_phone_input.value
                    confirm_phone_input.value = new_phone_input.value
                    page.show_snack_bar(ft.SnackBar(content=ft.Text("تم تحديث جهة الاتصال")))
                    page.dialog.open = False
                    page.update()
                else:
                    page.show_snack_bar(ft.SnackBar(content=ft.Text("يرجى إدخال الاسم ورقم الهاتف")))

            new_name_input = ft.TextField(label="الاسم الجديد", value=name, border_color=ft.colors.BLUE_400, focused_border_color=ft.colors.BLUE_700, border_radius=10)
            new_phone_input = ft.TextField(label="رقم الهاتف الجديد", value=phone_input.value, border_color=ft.colors.BLUE_400, focused_border_color=ft.colors.BLUE_700, border_radius=10)
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("تعديل جهة الاتصال"),
                content=ft.Column([new_name_input, new_phone_input], tight=True),
                actions=[
                    ft.TextButton("إلغاء", on_click=lambda _: close_dlg()),
                    ft.TextButton("حفظ", on_click=save_edit),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.dialog = dlg_modal
            dlg_modal.open = True
            page.update()
        else:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("لم يتم العثور على جهة الاتصال")))

    def delete_contact():
        if phone_input.value:
            cursor.execute("DELETE FROM contacts WHERE phone = ?", (phone_input.value,))
            conn.commit()
            clear_inputs()
            page.show_snack_bar(ft.SnackBar(content=ft.Text("تم حذف جهة الاتصال")))
        else:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("يرجى إدخال رقم الهاتف")))

    main_content = ft.Container(
        content=ft.Column([
            phone_input,
            suggestion_dropdown,
            confirm_phone_input,
            amount_input,
            action_row1,
            action_row2,
            ft.Row([call_button, copy_code_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([edit_button, delete_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]),
        padding=20,
        border_radius=20,
        bgcolor=ft.colors.BLUE_50
    )

    page.add(main_content)

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.BLUE,
            primary_container=ft.colors.BLUE_200,
            secondary=ft.colors.ORANGE,
            surface=ft.colors.BLUE_50,
        ),
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
    )

    page.update()

ft.app(target=main)
