#!/usr/bin/perl -w

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);

my $query = CGI->new();
# define the upload dir
my $upload_directory = '/tmp/';

if ($query->param('portrait')) {
	&print_page_start;
	&write_file;
	&print_page_end;
} else {
	&print_page_start;
	&print_form;
	&print_page_end;
}
# print the html sections 
sub print_page_start {
	print $query->header;
	print "<html><head><title>Portrait Upload</title></head>\n";
	print "<body>\n";
	print "<h1>Portarit Upload</h1>\n";
}

sub print_page_end {
	print "</body></html>\n";
}

sub print_form {
	print "<form action=\"upload.cgi\" method=\"post\" ";
	print "enctype=\"multipart/form-data\">\n";
	print "<input type=\"file\" name=\"portrait\" /><br/>\n";
	print "<input type=\"submit\" value=\"upload file\"><br/>\n";
	print "</form>\n";
}
# upload the file 
sub write_file {
	# take the file as a param 
	my $filename = $query->param('portrait');
	my $out_filename;
	my $counter = 0;
	my $buffer;
	# extracts the file name 
	if ($filename =~ m/.*[\/\\](.*)/gi) {
		$out_filename = $1;
	} else {
		$out_filename = $filename;
	}
	# program checks if the file exists and modifies the name with
	# the value of the counter
	while (-e "$upload_directory/$out_filename") {
		$counter++;
		$out_filename =~ s/^(.+)\.(.+)$/$1$counter\.$2/;
	}
	print "$filename<br />\n";
	# this prints the file on my server
	open (OUTFILE, ">", "$upload_directory/$out_filename") or die "Cannot open '$upload_directory/$out_filename' for writing: $!";binmode OUTFILE;
	while (my $bytesread = read ($filename, $buffer, 1024)) {
		 print OUTFILE $buffer;
	}
	close $filename;
	close OUTFILE;
}

sub print_success {
	print "<p>The file was saved successfully.</p>\n";
}
