' ============================================================
' Planilha "Rotinas tarefas do mes"
' Coloca a data de hoje na coluna B (Data da entrega) quando a
' coluna de status recebe "Realizado" ou "S/MOV". Se o status for apagado,
' a data também é apagada.
'
'   Aba Elen       -> status na coluna H
'   Aba Rosangela  -> status na coluna G
'   Aba Contabil   -> status na coluna F
'
' COLE ESTE CÓDIGO EM: EstaPasta_de_trabalho (ThisWorkbook)
' ============================================================

Private Sub Workbook_SheetChange(ByVal Sh As Object, ByVal Target As Range)
    Dim colStatus As String
    Select Case Sh.Name
        Case "Elen":      colStatus = "H"
        Case "Rosangela": colStatus = "G"
        Case "Contabil":  colStatus = "F"
        Case Else: Exit Sub
    End Select

    Dim area As Range, cel As Range
    Set area = Intersect(Target, Sh.Columns(colStatus))
    If area Is Nothing Then Exit Sub

    On Error GoTo Fim
    Application.EnableEvents = False

    For Each cel In area.Cells
        If cel.Row > 1 Then
            Dim st As String
            st = LCase(Trim(CStr(cel.Value)))
            If st = "realizado" Or st = "s/mov" Then
                ' só preenche se ainda não tiver data (não sobrescreve)
                If IsEmpty(Sh.Cells(cel.Row, "B").Value) Then
                    Sh.Cells(cel.Row, "B").Value = Date
                    Sh.Cells(cel.Row, "B").NumberFormat = "dd/mm/yyyy"
                End If
            ElseIf Trim(CStr(cel.Value)) = "" Then
                Sh.Cells(cel.Row, "B").ClearContents
            End If
        End If
    Next cel

Fim:
    Application.EnableEvents = True
End Sub
