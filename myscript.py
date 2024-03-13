from dpytools.http.upload import UploadClient

client = UploadClient("http://localhost:11850/upload")
client.upload(
    "tests/test_cases/countries.csv",
    "mybucket",
    "eyJraWQiOiJqeFlva3pnVER5UVVNb1VTM0c0ODNoa0VjY3hFSklKdCtHVjAraHVSRUpBPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI4ODkwYjY4NC02NzU4LTRiN2YtODFkOS1jYjkyYTMyODJiZjMiLCJjb2duaXRvOmdyb3VwcyI6WyJyb2xlLXB1Ymxpc2hlciJdLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtd2VzdC0yLmFtYXpvbmF3cy5jb21cL2V1LXdlc3QtMl9XU0Q5RWNBc3ciLCJjbGllbnRfaWQiOiI0ZXZsOTFnNHRzNWlzbXVkaHJjYmI0ZGFvYyIsIm9yaWdpbl9qdGkiOiIwMjYzOTQwNS04NGMzLTRmOTMtOGFkMy01MWMyZWJlOWExYjgiLCJldmVudF9pZCI6ImZlZjA5NDYyLWZiMmEtNDExNC1iYWU2LTg1OTFiYjAwM2YyZCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3MTAzNDU4NzYsImV4cCI6MTcxMDM0Njc3NiwiaWF0IjoxNzEwMzQ1ODc2LCJqdGkiOiJmOGZkZWE1Ni01M2E0LTRiZGItODZkMi04NDRkNjM0NmJjMmIiLCJ1c2VybmFtZSI6IjdkNTEzOWJjLTUyZGEtNDgxZi1hOTY0LTQ5MTkwYzRkZWNmMyJ9.AYrydwHidR6IpmFD068Rwv7h0NtcdGiyhga7cxKAHCCGYazbu9i-GzDjSPCwvc5rtfRS-wlfeqYIAGmLd-Koka21OdN0xbwVDl168ZxlgWKPsnLTWJ50oJV1B5oLZFz7qgs5szGz6oMbMvZxikoajJyVvaXn2CA2L0FHndFDqKHY-VV6kJbTX36-putjj4cd4umlSIwr81KKqOQsDdVtMEPL1YFL_5Tsuz3AzuJ2tpLn_025yKM9IkbnRAP5kH7oxROzJWx078774nIH0otRrjrChEaWkPAEU8peXTc-3FZDiuQd86RAbPASwPOhYhZz0kfzbnrk8Gg1UFgwnXnLKQ",
)
