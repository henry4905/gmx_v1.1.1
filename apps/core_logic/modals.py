from .helpers import get_notification

def get_modal_content(code=None, text=None, title="Ծանուցում"):
    """
    Ստեղծում է modal-ի HTML content:
    - code: NotificationTemplate.code DB-ից
    - text: ուղիղ տեքստ օգտագործելու դեպքում
    - title: modal-ի վերնագիր
    """
    if code:
        body_text = get_notification(code)
    elif text:
        body_text = text
    else:
        body_text = ""

    # Modal-ի HTML template
    modal_html = f"""
    <div class="custom-modal-overlay" id="customModal">
        <div class="custom-modal">
            <div class="custom-modal-header">
                <h3>{title}</h3>
                <span class="custom-modal-close" onclick="closeModal()">&times;</span>
            </div>
            <div class="custom-modal-body">
                {body_text}
            </div>
            <div class="custom-modal-footer">
                <button onclick="closeModal()">Փակել</button>
            </div>
        </div>
    </div>
    """
    return modal_html
    




""" ----------------------------------------------------------------
---------
-----------Դաշտերի տվյալները փոխելու համար նախատեսված մոդալ թեմփլեյթ 
---------
--------------------------------------------------------------------"""

