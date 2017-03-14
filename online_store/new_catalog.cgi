!/usr/bin/perl

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DBI;

my $query = CGI->new();

my $database = 'my_store';
my $db_server = 'localhost';
my $user = 'user';
my $password = 'pass';

my ($session_id, $dbh, $sth, $product_id, $quantity, $action);

if ($query->param('product_id')) {
	if ($query->cookie('session_id')) {
		$session_id = $query->cookie('session_id');
	} else {
		$session_id = time . $$;
	}
	set_variables();
	db_connect();
	print_page_start();
	add_to_cart();
	get_products();
	display_catalog();
	db_cleanup();
	print_page_end();

} else {
	print_page_start();
	db_connect();
	get_products();
	display_catalog();
	db_cleanup();
	print_page_end();
}

sub print_page_start {
	if ($session_id) {
		my $cookie = $query->cookie(-name => 'session_id',
									-value => $session_id);
		print $query->header(-cookie => $cookie);
	} else {
		print $query->header;
	}

	print "<html>\n<head>\n<title>PC Product Catalog</title>\n";
	print "</head>\n<body>\n";
	print "<h1 align=\"center\">PC Product Catalog</h1>\n";
}

sub db_connect {
	$dbh = DBI->connect("DBI:mysql:$database:$db_server", $user,$password);
}

sub get_products {
	my $sql_select = <<"MySQL";
	SELECT product_id, product_name, product_desc, product_price
	FROM products;
MySQL
	$sth = $dbh->prepare($sql_select) or die "Couldn’t prepare the query:", $sth->errstr, "\n";
	my $rv = $sth->execute or die "Couldn’t execute select statement: ", $sth->errstr, "\n";
}

sub display_catalog {
	print "<div align=\"center\">\n";
	print "<table border=\"1\" cellpadding=\"4\">\n";
	print "<tr>\n<th>Name</th>\n<th>Description</th>\n<th>Price</th>\n</tr>\n";

	while (my @row = $sth->fetchrow_array) {
		my ($product_id, $product_name, $product_desc,
		$product_price) = @row;
		print "<tr>\n";
		print "<form>\n";
		print "<input type=\"hidden\" name=\"product_id\" ";
		print "value=\"$product_id\" />\n";
		print "<td>$product_name</td>\n";
		print "<td>$product_desc</td>\n<td>$product_price</td>\n";
		print "<td><input type=\"text\" name=\"quantity\" ";
		print "value=\"1\" size=\"2\" /></td>\n";
		print "<td><input type=\"submit\" value=\"add\" /></td>\n";
		print "</form>\n";
		print "</tr>\n";
	}
	print "</table>\n</div>\n";
}

sub db_cleanup {
	my $rc = $dbh->disconnect;
}

sub print_page_end {
	print "<p align=\"center\"><b>";
	print"<a href=\"new_cart.cgi\">view cart</a></b></p>\n";
	print "</body>\n</html>\n";
}

sub set_variables {
	$product_id = $query->param('product_id');
	$quantity = $query->param('quantity');
}

sub add_to_cart {
	my $rec_quantity;

	# First, make sure they don’t already have the product
	# in their shopping cart. If they don’t have the cookie,
	# then it’s definitely not in their shopping cart.

	if ($query->cookie('session_id')) {
		# Since they have a session, let’s see if they
		# already have the product in their cart.
		my $sql_select = qq[SELECT quantity FROM cart 
		WHERE session_id = '$session_id' 
		AND product_id = $product_id];
		$sth = $dbh->prepare($sql_select) or die "Couldn’t prepare the query:", $sth->errstr, "\n";
		my $rv = $sth->execute or die "Couldn’t execute select statement: ", $sth->errstr, "\n";

		# If a record was found, we need to update it.
		# Otherwise we can just insert a new record.
		if (($rec_quantity) = $sth->fetchrow_array) {
			$action = "update";
		} else {
			$action = "insert";
		}
	} else {
		$action = "insert";
	}

	if ($action eq 'insert') {
		my $sql_insert = qq[INSERT INTO cart (session_id, product_id, quantity)
			VALUES (?, ?, ?)];
		$sth = $dbh->prepare($sql_insert) or die "Couldn’t prepare the query:", $sth->errstr, "\n";
		$sth->execute($session_id, $product_id, $quantity) or die "Couldn’t prepare the query:", $sth->errstr, "\n";
	} else {
		my $new_quantity = $quantity + $rec_quantity;
		my $sql_update = qq[UPDATE cart SET quantity = ?
			WHERE session_id = $session_id AND product_id = $product_id];
		$sth = $dbh->prepare($sql_update) or die "Couldn’t prepare the query:", $sth->errstr, "\n";
		my $rv = $sth->execute($quantity) or die "Couldn’t prepare the query:", $sth->errstr, "\n";
		my $rc = $sth->finish;
	}
	
}

