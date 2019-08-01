def Outlook (To, Subject, Body, AttachmentPath) :
    import win32com.client as win32
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = To
    mail.Subject = Subject
    mail.Body = Body

    #To attach a file to the email (optional):

    mail.Attachments.Add(AttachmentPath)

    mail.Send()

