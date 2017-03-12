#!/usr/bin/perl -w

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);

my $query = CGI->new();

my $file = 'products.txt';
my $cart_file = '/tmp/cart.txt';

my ($session_id, $page_title, $action);
my @user_cart;
my %product_names;
my %product_prices;

if ($query->cookie('session_id')) {
	$session_id = ($query->cookie('session_id'));
}

if ($query->param('action')) {
	$action = $query->param('action');
	if ($query->param('action') eq 'remove') {
		$page_title = "Shopping Cart";
		my $val = $query->param('action');
		print "<p>|$val|</p>\n";
		remove_item();
		print_page_start();
		get_cart_contents();
	}

	if (@user_cart) {
		get_product_list();
		print_cart();	
	} else {
		print_no_cart();
	}
	print_page_end();
}  else {
	$page_title = "Shopping Cart";
	print_page_start();
	get_cart_contents();
	if (@user_cart) {
		get_product_list();
		print_cart();
	}
	else {
		print_no_cart();
	}
	print_page_end();
}

sub remove_item {
	chdir;
	open (CART, '+<', $cart_file) or die "Could not open? '$cart_file' $!:";
	flock CART, 2;
	seek CART, 0, 0;
	my @records = <CART>;
	my @new_records = ();
	foreach my $record (@records) {
		chomp $record;
		my ($rec_session_id, $rec_product_id, $rec_quantity) = split /:/, $record;
		unless (($rec_session_id eq $session_id) and
			($rec_product_id eq $query->param('product_id'))) {
			push @new_records, $record . "\n";
		}
	}
	seek CART, 0, 0;
	truncate CART, 0;
	print CART @new_records;
	close CART;
}

sub get_cart_contents {
	open (CART, '+<', $cart_file) or die "Could not open? '$cart_file' $!:";

	my @records = <CART>;
	@user_cart = ();
	foreach my $record (@records) {
		chomp $record;
		my ($rec_session_id, $rec_product_id, $rec_quantity) = split /:/, $record;

		if ($rec_session_id eq $session_id) {
			push @user_cart, $record;
		}
	}
}

sub get_product_list {
	open (CATALOG, '<', $file) or die "Cant open '$file' $!:";
	%product_names = ();
	%product_prices = ();
	while (my $line = <CATALOG>) {
		chomp $line;
		my ($cart_product_id, $product_name, $product_price) = split /:/, $line;
		
		$product_names{$cart_product_id} = $product_name;
		$product_prices{$cart_product_id} = $product_price;
	}
	close CATALOG;
}

sub print_cart {
	print "<div align=\"center\">\n<table>\n<tr>\n";

	print "<th>Product ID</th>\n<th>Product Name</th>\n";
	print "<th>Price</th>\n<th>Quantity</th>\n</tr>\n";
	foreach my $cart_item (@user_cart) {
		my ($rec_session_id, $rec_product_id, $rec_quantity) = split /:/, $cart_item;
	
		print "<td>$rec_product_id</td>\n";
		print "<td>", $product_names{$rec_product_id}, "</td>\n";
		print "<td>", $product_prices{$rec_product_id}, "</td>\n";
		print "<td>$rec_quantity</td>\n";
		print "<td>\n<form>\n";
		print "<input type=\"hidden\" name=\"action\" ";
		print "value=\"remove\" />\n";
		print "<input type=\"hidden\" name=\"product_id\" ";
		print "value=\"$rec_product_id\" />\n";
		print "<input type=\"submit\" value=\"remove\" />\n";
		print "</td>\n";
		print "</TR>\n";
	}
	print "</table></div>\n";
}

sub print_page_start {
	print $query->header;
	print "<html>\n<head>\n<title>$page_title</title>\n";
	print "</head>\n<body>\n";
	print "<h1 align=\"center\">$page_title</h1>\n";
}
sub print_no_cart {
	print "<p>There are no items in your shopping cart.</p>\n";
}
sub print_page_end {
	print "<p><div align=\"center\"><b>";
	print "<a href=\"catalog.cgi\">return to catalog</a></b><br />\n";
	print "<b><a href=\"checkout.cgi\">check out</a></b>\n";
	print "</div></p>\n";
	print "</body>\n</html>\n";
}
