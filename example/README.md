
Run myapp.py first.

Start using the remote console:

```
PS C:\Users\wangyueheng> py -3 -m remoteconsole.client
>>> a = 10
>>> b = 20
>>> a + b
30
>>> import __main__
>>> __main__.app
<__main__.MyApp object at 0x000001D1454B99A0>
>>> __main__.app.label.configure(text='world')  # the label text will change
>>> import myutil
>>> myutil.f1()
call f1
>>> myutil.f2()
'some value'
```
