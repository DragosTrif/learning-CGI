#!/usr/bin/perl -wT

use strict;

use CGI qw/:standard/;

my $cookie_1 = cookie(-value =>'testcokie',value =>'testvalue',expires =>'+7d');
my $cookie_2 = cookie(-value =>'secondcookie',value =>'secondval',expires =>'+1d');

print header (-cookie=>[$cookie_1,$cookie_2]),
start_html('Cgi cookie test'),
p("You recived a cookie\n"),
end_html;
