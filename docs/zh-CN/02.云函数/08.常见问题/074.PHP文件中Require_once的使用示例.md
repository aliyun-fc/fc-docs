# PHP文件中Require_once的使用示例

- a.php
  
  使用示例如下：
  
  ```
  <?php $appcode = 123456; class Foo { public $name = 'FooClass'; function sayhi() { print 'Foo say hello!'; } } $foo = new Foo;
  ```
- b.php
  
  使用示例如下：
  
  ```
  <?php require_once __DIR__ . '/a.php'; function handler($event, $context) { echo $GLOBALS['appcode'] . PHP_EOL; $GLOBALS['foo']->sayhi(); $foo2 = new Foo; $foo2->sayhi(); return $GLOBALS['appcode']; }
  ```
