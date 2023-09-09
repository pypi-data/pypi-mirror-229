<!-- markdownlint-disable -->

<a href="..\..\qtstrap\widgets\toggle.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `widgets.toggle`




**Global Variables**
---------------
- **TYPE_CHECKING**
- **PYQT6**
- **PYQT5**
- **PYSIDE2**
- **PYSIDE6**


---

<a href="..\..\qtstrap\widgets\toggle.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Toggle`




<a href="..\..\qtstrap\widgets\toggle.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Toggle.__init__`

```python
__init__(
    *args,
    bar_color=PySide2.QtCore.Qt.GlobalColor.gray,
    checked_color='#00B0FF',
    handle_color=PySide2.QtCore.Qt.GlobalColor.white,
    **kwargs
)
```








---

<a href="..\..\qtstrap\widgets\toggle.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Toggle.handle_state_change`

```python
handle_state_change(value)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Toggle.hitButton`

```python
hitButton(pos: PySide2.QtCore.QPoint)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Toggle.paintEvent`

```python
paintEvent(e: PySide2.QtGui.QPaintEvent)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `Toggle.sizeHint`

```python
sizeHint()
```






---

<a href="..\..\qtstrap\widgets\toggle.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AnimatedToggle`




<a href="..\..\qtstrap\widgets\toggle.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `AnimatedToggle.__init__`

```python
__init__(
    *args,
    pulse_unchecked_color='#44999999',
    pulse_checked_color='#4400B0EE',
    **kwargs
)
```








---

<a href="..\..\qtstrap\widgets\toggle.py#L143"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `AnimatedToggle.handle_state_change`

```python
handle_state_change(value)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `AnimatedToggle.hitButton`

```python
hitButton(pos: PySide2.QtCore.QPoint)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L152"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `AnimatedToggle.paintEvent`

```python
paintEvent(e: PySide2.QtGui.QPaintEvent)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `AnimatedToggle.sizeHint`

```python
sizeHint()
```






---

<a href="..\..\qtstrap\widgets\toggle.py#L204"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PersistentToggle`




<a href="..\..\qtstrap\widgets\toggle.py#L205"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentToggle.__init__`

```python
__init__(name, changed=None, *args, **kwargs)
```








---

<a href="..\..\qtstrap\widgets\toggle.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentToggle.handle_state_change`

```python
handle_state_change(value)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentToggle.hitButton`

```python
hitButton(pos: PySide2.QtCore.QPoint)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentToggle.paintEvent`

```python
paintEvent(e: PySide2.QtGui.QPaintEvent)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L215"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentToggle.restore_state`

```python
restore_state()
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentToggle.sizeHint`

```python
sizeHint()
```






---

<a href="..\..\qtstrap\widgets\toggle.py#L223"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PersistentAnimatedToggle`




<a href="..\..\qtstrap\widgets\toggle.py#L224"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentAnimatedToggle.__init__`

```python
__init__(name, changed=None, *args, **kwargs)
```








---

<a href="..\..\qtstrap\widgets\toggle.py#L143"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentAnimatedToggle.handle_state_change`

```python
handle_state_change(value)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentAnimatedToggle.hitButton`

```python
hitButton(pos: PySide2.QtCore.QPoint)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L152"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentAnimatedToggle.paintEvent`

```python
paintEvent(e: PySide2.QtGui.QPaintEvent)
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L234"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentAnimatedToggle.restore_state`

```python
restore_state()
```





---

<a href="..\..\qtstrap\widgets\toggle.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `PersistentAnimatedToggle.sizeHint`

```python
sizeHint()
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
