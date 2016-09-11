<?php
header('Location: https://box1147.bluehost.com/~weiksner/perfectpractice/name.html?instrument=' . $_GET['instrument'] . '&book=' . $_GET['book']);

$appear_url = 'https://appear.in/' . $_GET['instrument'] . $_GET['book'];

system("/home1/weiksner/python27/bin/python test.py " . $appear_url );

?>
