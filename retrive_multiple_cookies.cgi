#!/usr/bin/perl -w

use strict;

use CGI qw/:standard/;

my $retrievedcookie1 = cookie('testcookie2');
my $retrievedcookie2 = cookie('secondcookie');

print header,
start_html,
p("You sent a couple cookies and their values were |$retrievedcookie1| and |$retrievedcookie2|\n"),
end_html;
