#!/usr/bin/perl

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DBI;

my $query = CGI->new();

my $database = 'my_store';
my $db_server = 'localhost';
my $user = 'root';
my $password = 1;

my ($session_id, $page_title, $dbh, $sth);

if ($query->cookie('session_id')) {
	$session_id = ($query->cookie('session_id'));
}

if ($query->param('action')) {
	if ($query->param('action') eq 'remove') {
		$page_title = "Shopping Cart";
		db_connect();
		remove_item();
		print_page_start();
		if ($sth->rows) {
			print_cart();
		}
		else {
			print_no_cart();
		}
		print_page_end();
		db_cleanup();
	}
} else {
	$page_title = "Shopping Cart";
	print_page_start();
	db_connect();
	get_cart_contents();
	if ($sth->rows) {
		print_cart();
	}
	else {
		print_no_cart();
	}
	print_page_end();
	db_cleanup();
}

sub print_page_start {
	print $query->header;
	print "<html>\n<head>\n<title>$page_title</title>\n";
	print "</head>\n<body>\n";
	print "<h1 aligh=\"center\">$page_title</h1>\n";
}

sub db_connect {
	$dbh = DBI->connect("DBI:mysql:$database:$db_server", $user,$password);
}

sub get_cart_contents {
	my $sql_select = qq[SELECT cart.product_id,
		quantity, product_name, product_price
		FROM cart, products
		WHERE session_id = ?
		AND cart.product_id = products.product_id];
	$sth = $dbh->prepare($sql_select) or die "Couldn’t prepare the query:", $sth->errstr, "\n";
	my $rv = $sth->execute($session_id) or die "Couldn’t prepare the query:", $sth->errstr, "\n";
}

sub print_cart {
	print "<div align=\"center\">\n<table>\n<tr>\n";
	print "<th>Product ID</th>\n<th>Product Name</th>\n";
	print "<th>Price</th>\n<th>Quantity</th>\n</tr>\n";
	while (my @row = $sth->fetchrow_array) {
		my ($rec_product_id, $rec_quantity, $rec_product_name,
		$rec_price) = @row;
		print "<td>$rec_product_id</td>\n";
		print "<td>$rec_product_name</td>\n";
		print "<td>$rec_price</td>\n";
		print "<td>$rec_quantity</td>\n";
		print "<td>\n<form>\n";
		print "<input type=\"hidden\" name=\"action\" ";
		print "value=\"remove\" />\n";
		print "<input type=\"hidden\" name=\"product_id\" ";
		print "value=\"$rec_product_id\" />\n";
		print "<input type=\"submit\" value=\"remove\" />\n";
		print "</td>\n";
		print "</tr>\n";
	}
	print "</table>\n";
}

sub print_no_cart {
	print "<p>There are no items in your shopping cart.</p>\n";
}

sub print_page_end {
	print "<center>";
	print "<p><b><a href=\"new_catalog.cgi\">return to catalog</a></b></p>\n";
	print "<p><b><a href=\"new_checkout.cgi\">check out</a></b></p>\n";
	print "</center>";
	print "</body>\n</html>\n";
}

sub db_cleanup {
	my $rc = $dbh->disconnect;
} 

sub remove_item {
	my $product_id = $query->param('product_id');
	my $sql_delete = qq[DELETE FROM cart
		WHERE session_id = ?
		AND product_id = ?];
	$sth = $dbh->prepare($sql_delete) or die "Couldn’t prepare the query:", $sth->errstr, "\n";
	my $rv = $sth->execute($session_id, $product_id) or die "Couldn’t exectute the query:", $sth->errstr, "\n";
}
